package main

// ADR-0046 tests. The real thing (namespaces, a cgroup2 mount, the drop to
// uid 10001) needs a container and is proven by the bake-off; these pin the
// two pieces that decide the security outcome and run anywhere: which files
// the judge user is given, and the "no capabilities" check.

import (
	"os"
	"path/filepath"
	"sort"
	"strings"
	"testing"
)

// fakeCgroup lays out the files cgroupfs would create on mkdir, so the
// setup can run on a plain directory. A restarted container sees the same:
// the tree is already there.
func fakeCgroup(t *testing.T, procs string) string {
	t.Helper()
	root := t.TempDir()
	files := map[string]string{
		"cgroup.procs":                    procs,
		"cgroup.subtree_control":          "",
		"init/cgroup.procs":               "",
		"rankwant/cgroup.procs":           "",
		"rankwant/cgroup.subtree_control": "",
		"rankwant/cgroup.threads":         "",
		"rankwant/pids.max":               "max",
		"rankwant/memory.max":             "max",
		"rankwant/memory.swap.max":        "max",
		"rankwant/svc/cgroup.procs":       "",
	}
	for rel, body := range files {
		path := filepath.Join(root, rel)
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(body), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	return root
}

func read(t *testing.T, path string) string {
	t.Helper()
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return string(data)
}

func TestSetupDelegatedCgroupLayout(t *testing.T) {
	root := fakeCgroup(t, "1\n7\n")
	var owned []string
	chown := func(path string, uid, gid int) error {
		if uid != judgeUID || gid != judgeGID {
			t.Errorf("%s: chown %d:%d, want %d:%d", path, uid, gid, judgeUID, judgeGID)
		}
		rel, _ := filepath.Rel(root, path)
		owned = append(owned, filepath.ToSlash(rel))
		return nil
	}
	if err := setupDelegatedCgroup(root, judgeUID, judgeGID, 42, chown); err != nil {
		t.Fatalf("setup: %v", err)
	}

	// The worker lands inside the delegated subtree, not next to it:
	// otherwise it may not move a sandbox into a run cgroup.
	if got := read(t, filepath.Join(root, "rankwant/svc/cgroup.procs")); got != "42" {
		t.Errorf("worker pid in rankwant/svc = %q, want 42", got)
	}
	for _, rel := range []string{"cgroup.subtree_control", "rankwant/cgroup.subtree_control"} {
		if got := read(t, filepath.Join(root, rel)); got != "+cpu +memory +pids" {
			t.Errorf("%s = %q", rel, got)
		}
	}
	// The ceiling is written by root before the drop.
	for rel, want := range map[string]string{
		"rankwant/pids.max":        parentPidsMax,
		"rankwant/memory.max":      parentMemMaxStr,
		"rankwant/memory.swap.max": "0",
	} {
		if got := read(t, filepath.Join(root, rel)); got != want {
			t.Errorf("%s = %q, want %q", rel, got, want)
		}
	}

	// Exactly the delegation files — never the ceiling, never the root.
	sort.Strings(owned)
	want := []string{
		"rankwant",
		"rankwant/cgroup.procs",
		"rankwant/cgroup.subtree_control",
		"rankwant/cgroup.threads",
		"rankwant/svc",
		"rankwant/svc/cgroup.procs",
	}
	if strings.Join(owned, ",") != strings.Join(want, ",") {
		t.Errorf("chowned %v\nwant    %v", owned, want)
	}
	for _, path := range owned {
		if strings.HasSuffix(path, ".max") || !strings.HasPrefix(path, "rankwant") {
			t.Errorf("judge user given %s — it could lift its own limits", path)
		}
	}
}

// A failed hand-over must stop the worker, not let it run on a tree it
// cannot limit.
func TestSetupDelegatedCgroupFailsClosed(t *testing.T) {
	root := fakeCgroup(t, "1\n")
	deny := func(string, int, int) error { return os.ErrPermission }
	if err := setupDelegatedCgroup(root, judgeUID, judgeGID, 42, deny); err == nil {
		t.Fatal("chown failed, but setup reported success")
	}
	if got := read(t, filepath.Join(root, "rankwant/svc/cgroup.procs")); got != "" {
		t.Errorf("worker moved into the subtree after a failed hand-over: %q", got)
	}
}

func TestSetupDelegatedCgroupRejectsGarbagePids(t *testing.T) {
	root := fakeCgroup(t, "1\nnot-a-pid\n")
	ok := func(string, int, int) error { return nil }
	if err := setupDelegatedCgroup(root, judgeUID, judgeGID, 42, ok); err == nil {
		t.Fatal("unreadable cgroup.procs accepted")
	}
}

func TestCapEff(t *testing.T) {
	status := "Name:\tjudge-go\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000000\n" +
		"CapEff:\t00000000800000c0\nCapBnd:\t00000000800000c0\n"
	got, err := capEff(status)
	if err != nil || got != 0x800000c0 {
		t.Fatalf("capEff = %x, %v; want 800000c0", got, err)
	}
	if _, err := capEff("Name:\tx\n"); err == nil {
		t.Fatal("missing CapEff line read as no capabilities")
	}
}

func TestCheckUIDMap(t *testing.T) {
	for _, tc := range []struct {
		uidMap   string
		rootless bool
		ok       bool
	}{
		{"     65534      10001          1\n", true, true},
		{"     65534          0          1\n", false, true}, // the privileged layout, launcher off
		{"     65534          0          1\n", true, false}, // launcher on, sandbox still root outside
		{"", true, false},
		{"0 0 4294967295\n", false, false}, // no user namespace at all
	} {
		err := checkUIDMap(tc.uidMap, tc.rootless)
		if (err == nil) != tc.ok {
			t.Errorf("checkUIDMap(%q, rootless=%v) = %v, want ok=%v", tc.uidMap, tc.rootless, err, tc.ok)
		}
	}
}

// The sandbox policy is part of the isolation: a refactor that drops it
// leaves every other check green (bake-off 33 is the dynamic proof).
func TestSandboxSeccompIsPassed(t *testing.T) {
	args := strings.Join(nsjailArgs("/w", Limits{}, 1), " ")
	if !strings.Contains(args, "--seccomp_string "+sandboxSeccomp) {
		t.Fatal("nsjail runs without the sandbox seccomp policy")
	}
	for _, name := range []string{"mount", "umount", "pivot_root", "unshare", "setns", "clone3", "0x7e020000"} {
		if !strings.Contains(sandboxSeccomp, name) {
			t.Errorf("sandbox policy no longer closes %s", name)
		}
	}
}

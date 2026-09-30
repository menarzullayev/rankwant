"""Canonical A+B file-I/O solutions (input.txt → output.txt) for all judge languages.

Verified via `tools/submit_aplus_matrix.py --file` on `a-plus-b` (io_mode=both).
"""

from __future__ import annotations

from aplus_solutions import APLUS

IN_FILE = "input.txt"
OUT_FILE = "output.txt"

APLUS_FILE: dict[str, str] = {
    "cpp23": """#include <bits/stdc++.h>
using namespace std;

int main() {
    ifstream in("input.txt");
    ofstream out("output.txt");
    long long a, b;
    if (!(in >> a >> b)) return 0;
    out << a + b;
    return 0;
}
""",
    "c17": """#include <stdio.h>

int main(void) {
    FILE *in = fopen("input.txt", "r");
    FILE *out = fopen("output.txt", "w");
    if (!in || !out) return 1;
    long long a, b;
    if (fscanf(in, "%lld %lld", &a, &b) != 2) return 0;
    fprintf(out, "%lld", a + b);
    fclose(in);
    fclose(out);
    return 0;
}
""",
    "py313": """from pathlib import Path

data = Path("input.txt").read_text().split()
if len(data) >= 2:
    Path("output.txt").write_text(str(int(data[0]) + int(data[1])))
""",
    "pypy73": """from pathlib import Path

data = Path("input.txt").read_text().split()
if len(data) >= 2:
    Path("output.txt").write_text(str(int(data[0]) + int(data[1])))
""",
    "java21": """import java.io.*;
import java.nio.file.*;

public class Main {
    public static void main(String[] args) throws Exception {
        var line = Files.readString(Path.of("input.txt")).trim();
        var st = new java.util.StringTokenizer(line);
        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());
        Files.writeString(Path.of("output.txt"), Long.toString(a + b));
    }
}
""",
    "js24": """const fs = require("fs");
const input = fs.readFileSync("input.txt", "utf8").trim().split(/\\s+/);
if (input.length >= 2) {
  fs.writeFileSync("output.txt", String(Number(input[0]) + Number(input[1])));
}
""",
    "ts24": """const fs = require("fs");
const input = fs.readFileSync("input.txt", "utf8").trim().split(/\\s+/);
if (input.length >= 2) {
  fs.writeFileSync("output.txt", String(Number(input[0]) + Number(input[1])));
}
""",
    "csharp14": """using System.IO;

class Program {
    static void Main() {
        var line = File.ReadAllText("input.txt").Trim();
        var sp = line.IndexOf(' ');
        var a = long.Parse(line.Substring(0, sp));
        var b = long.Parse(line.Substring(sp + 1).Trim());
        File.WriteAllText("output.txt", (a + b).ToString());
    }
}
""",
    "go124": """package main

import (
    "fmt"
    "os"
)

func main() {
    data, err := os.ReadFile("input.txt")
    if err != nil {
        return
    }
    var a, b int64
    if _, err := fmt.Sscan(string(data), &a, &b); err != nil {
        return
    }
    _ = os.WriteFile("output.txt", []byte(fmt.Sprintf("%d", a+b)), 0o644)
}
""",
    "rust185": """use std::fs;

fn main() {
    let s = fs::read_to_string("input.txt").unwrap();
    let mut it = s.split_whitespace();
    let a: i64 = it.next().unwrap().parse().unwrap();
    let b: i64 = it.next().unwrap().parse().unwrap();
    fs::write("output.txt", format!("{}", a + b)).unwrap();
}
""",
    "kotlin24": """fun main() {
    val parts = java.io.File("input.txt").readText().trim().split(" ")
    val sum = parts[0].toLong() + parts[1].toLong()
    java.io.File("output.txt").writeText(sum.toString())
}
""",
    "php84": """<?php
$in = trim(file_get_contents("input.txt"));
if ($in === '') { exit(0); }
$parts = preg_split('/\\s+/', $in);
file_put_contents("output.txt", (string)((int)$parts[0] + (int)$parts[1]));
""",
    "ruby33": """line = File.read("input.txt")
a, b = line.split.map(&:to_i)
File.write("output.txt", (a + b).to_s)
""",
    "pascal322": """program Main;
var a, b: int64;
    fin: text;
    fout: text;
begin
  assign(fin, 'input.txt');
  reset(fin);
  readln(fin, a, b);
  close(fin);
  assign(fout, 'output.txt');
  rewrite(fout);
  write(fout, a + b);
  close(fout);
end.
""",
    "swift60": """import Glibc

var inFd = open("input.txt", O_RDONLY)
var buf = [UInt8](repeating: 0, count: 128)
let n = read(inFd, &buf, buf.count)
close(inFd)
var s = String(decoding: buf.prefix(Int(n)), as: UTF8.self)
while let last = s.last, last == "\\n" || last == " " || last == "\\t" {
    s.removeLast()
}
let parts = s.split(separator: " ")
let sum = Int64(parts[0])! + Int64(parts[1])!
var outStr = String(sum)
var outFd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0o644)
outStr.withUTF8 { _ = write(outFd, $0.baseAddress, $0.count) }
close(outFd)
""",
    "dart313": """import 'dart:io';

void main() {
  final parts = File('input.txt').readAsStringSync().trim().split(RegExp(r'\\s+'));
  File('output.txt').writeAsStringSync('${int.parse(parts[0]) + int.parse(parts[1])}');
}
""",
    "haskell96": """main = do
  line <- readFile "input.txt"
  let [sa, sb] = words line
  writeFile "output.txt" (show (read sa + read sb :: Integer))
""",
    "r45": """p <- scan("input.txt", what = numeric(), n = 2, quiet = TRUE)
cat(format(p[1] + p[2], scientific = FALSE, trim = TRUE), file = "output.txt")
""",
    "perl540": """open my $in, '<', 'input.txt' or exit 1;
my $line = <$in>;
close $in;
chomp $line;
my ($a, $b) = split ' ', $line;
open my $out, '>', 'output.txt' or exit 1;
print $out $a + $b;
close $out;
""",
    "d140": """import std.array;
import std.conv;
import std.format;
import std.file;

void main() {
    auto parts = readText("input.txt").split();
    long a = to!long(parts[0]);
    long b = to!long(parts[1]);
    write("output.txt", format("%s", a + b));
}
""",
    "ocaml53": """let () =
  let ic = open_in "input.txt" in
  let line = input_line ic in
  close_in ic;
  Scanf.sscanf line "%Ld %Ld" (fun a b ->
    let oc = open_out "output.txt" in
    Printf.fprintf oc "%Ld" (Int64.add a b);
    close_out oc)
""",
    "caml53": """let () =
  let ic = open_in "input.txt" in
  let line = input_line ic in
  close_in ic;
  Scanf.sscanf line "%Ld %Ld" (fun a b ->
    let oc = open_out "output.txt" in
    Printf.fprintf oc "%Ld" (Int64.add a b);
    close_out oc)
""",
    "scala39": """object Main {
  def main(args: Array[String]): Unit = {
    val p = scala.io.Source.fromFile("input.txt").getLines().next().split(" ")
    val out = new java.io.PrintWriter("output.txt")
    out.print(p(0).toLong + p(1).toLong)
    out.close()
  }
}
""",
    "vbnet17": """Imports System.IO

Module Program
    Sub Main()
        Dim line = File.ReadAllText("input.txt").Trim()
        Dim sp = line.IndexOf(" "c)
        Dim a = Long.Parse(line.Substring(0, sp))
        Dim b = Long.Parse(line.Substring(sp + 1).Trim())
        File.WriteAllText("output.txt", (a + b).ToString())
    End Sub
End Module
""",
    "fortran14": """program main
  implicit none
  integer(8) :: a, b
  open(10, file='input.txt', status='old')
  read(10, *) a, b
  close(10)
  open(11, file='output.txt', status='replace')
  write(11, '(I0)', advance='no') a + b
  close(11)
end program main
""",
    "ada14": """with Ada.Text_IO;
with Ada.Long_Long_Integer_Text_IO;

procedure Main is
   InF, OutF : Ada.Text_IO.File_Type;
   A, B : Long_Long_Integer;
begin
   Ada.Text_IO.Open (InF, Ada.Text_IO.In_File, "input.txt");
   Ada.Long_Long_Integer_Text_IO.Get (InF, A);
   Ada.Long_Long_Integer_Text_IO.Get (InF, B);
   Ada.Text_IO.Close (InF);
   Ada.Text_IO.Create (OutF, Ada.Text_IO.Out_File, "output.txt");
   Ada.Long_Long_Integer_Text_IO.Put (OutF, A + B, Width => 0);
   Ada.Text_IO.Close (OutF);
end Main;
""",
    "objc14": """#import <stdio.h>

int main(void) {
    FILE *in = fopen("input.txt", "r");
    FILE *out = fopen("output.txt", "w");
    if (!in || !out) return 1;
    long long a, b;
    if (fscanf(in, "%lld %lld", &a, &b) != 2) return 0;
    fprintf(out, "%lld", a + b);
    fclose(in);
    fclose(out);
    return 0;
}
""",
}

# COBOL / NASM / Julia / Prolog / Lua / PS / Lisp / F# — uzun; alohida qo'shiladi.
APLUS_FILE.update(
    {
        "julia113": """function solve()
    s = read("input.txt", String)
    sp = findfirst(' ', s)
    a = parse(Int64, s[1:sp - 1])
    b = parse(Int64, s[sp + 1:end])
    open("output.txt", "w") do io
        print(io, a + b)
    end
end
solve()
""",
        "prolog92": """:- initialization(main, main).

main :-
    setup_call_cleanup(
        open('input.txt', read, In, []),
        ( read_line_to_string(In, Line),
          split_string(Line, " ", " \\t", Parts),
          maplist(number_string, [A, B], Parts),
          Sum is A + B,
          setup_call_cleanup(
              open('output.txt', write, Out, []),
              format(Out, '~w', [Sum]),
              close(Out))
        ),
        close(In)).
""",
        "lua54": """local f = io.open("input.txt", "r")
local line = f:read("*l")
f:close()
local a, b = line:match("(%S+)%s+(%S+)")
local out = io.open("output.txt", "w")
out:write(tonumber(a) + tonumber(b))
out:close()
""",
        "powershell76": """$line = Get-Content -Path "input.txt" -TotalCount 1
$parts = $line.Split(' ', [StringSplitOptions]::RemoveEmptyEntries)
Set-Content -Path "output.txt" -Value ([int64]$parts[0] + [int64]$parts[1]) -NoNewline
""",
        "lisp25": """(with-open-file (in "input.txt" :direction :input)
  (let* ((a (read in))
         (b (read in)))
    (with-open-file (out "output.txt" :direction :output :if-exists :supersede)
      (princ (+ a b) out))))
""",
        "fsharp10": """[<EntryPoint>]
let main _ =
    let parts = System.IO.File.ReadAllText("input.txt").Trim().Split(' ')
    System.IO.File.WriteAllText("output.txt", string (int64 parts.[0] + int64 parts.[1]))
    0
""",
    }
)

# COBOL: stdin yechimidagi formatlash mantig'i saqlanadi.
APLUS_FILE["cobol32"] = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. MAIN.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IN-FILE ASSIGN TO "input.txt"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT OUT-FILE ASSIGN TO "output.txt"
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD IN-FILE.
       01 IN-REC PIC X(128).
       FD OUT-FILE.
       01 OUT-REC PIC X(128).
       WORKING-STORAGE SECTION.
       01 A PIC S9(18) COMP-5.
       01 B PIC S9(18) COMP-5.
       01 WS-TOTAL PIC S9(18) COMP-5.
       01 WS-OUT PIC -Z(18)9.
       01 WS-RAW PIC X(21).
       01 WS-DIS PIC X(24).
       01 WS-IDX PIC 9(2) VALUE 1.
       01 WS-LEN PIC 9(2) VALUE 0.
       PROCEDURE DIVISION.
           OPEN INPUT IN-FILE
           READ IN-FILE INTO IN-REC
           CLOSE IN-FILE
           UNSTRING IN-REC DELIMITED BY ALL SPACE
               INTO A B
           COMPUTE WS-TOTAL = A + B
           MOVE WS-TOTAL TO WS-OUT
           MOVE WS-OUT TO WS-RAW
           MOVE SPACES TO WS-DIS
           PERFORM VARYING WS-IDX FROM 1 BY 1 UNTIL WS-IDX > 21
               IF WS-RAW(WS-IDX:1) NOT = SPACE
                   ADD 1 TO WS-LEN
                   MOVE WS-RAW(WS-IDX:1) TO WS-DIS(WS-LEN:1)
               END-IF
           END-PERFORM
           OPEN OUTPUT OUT-FILE
           WRITE OUT-REC FROM WS-DIS(1:WS-LEN)
           CLOSE OUT-FILE
           STOP RUN.
"""

# NASM: input.txt dan o'qiydi, output.txt ga yozadi (print_int barcha chiqish shu fd ga).
_NASM_FILE = r"""default rel
section .bss
inbuf: resb 64
outbuf: resb 32

section .data
inpath: db "input.txt",0
outpath: db "output.txt",0

section .text
global _start

_start:
    mov rdi, inpath
    xor rsi, rsi
    mov rax, 2
    syscall
    mov r8, rax
    mov rax, 0
    mov rdi, r8
    mov rsi, inbuf
    mov rdx, 64
    syscall
    mov rbx, rax
    cmp rbx, 63
    ja .nulskip
    mov byte [inbuf + rbx], 0
.nulskip:
    mov rax, 3
    mov rdi, r8
    syscall
    mov rdi, inbuf
    call parse_int
    mov r12, rax
    call skip_sep
    call parse_int
    add rax, r12
    mov r13, rax
    mov rdi, outpath
    mov rsi, 577
    mov rdx, 420
    mov rax, 2
    syscall
    mov r8, rax
    mov rax, r13
    call print_int
    mov rax, 3
    mov rdi, r8
    syscall
    mov rax, 60
    xor rdi, rdi
    syscall

skip_sep:
.s:
    mov al, [rdi]
    cmp al, '-'
    je .ret
    cmp al, '0'
    jb .n
    cmp al, '9'
    jbe .ret
.n:
    cmp byte [rdi], 0
    je .ret
    cmp byte [rdi], 10
    je .ret
    inc rdi
    jmp .s
.ret:
    ret

parse_int:
    xor rax, rax
    xor r11, r11
    cmp byte [rdi], '-'
    jne .pos
    mov r11, 1
    inc rdi
.pos:
.loop:
    movzx rcx, byte [rdi]
    cmp cl, '0'
    jb .done
    cmp cl, '9'
    ja .done
    imul rax, rax, 10
    sub cl, '0'
    add rax, rcx
    inc rdi
    jmp .loop
.done:
    test r11, r11
    jz .ret
    neg rax
.ret:
    ret

print_int:
    cmp rax, 0
    jne .nz
    mov byte [outbuf], '0'
    mov rsi, outbuf
    mov rdx, 1
    jmp .write
.nz:
    test rax, rax
    jns .pos
    mov byte [outbuf], '-'
    mov rsi, outbuf
    mov rdx, 1
    push rax
    mov rax, 1
    mov rdi, r8
    syscall
    pop rax
    neg rax
.pos:
    mov rbx, outbuf
    add rbx, 31
    xor r13, r13
.loop:
    xor rdx, rdx
    mov rcx, 10
    div rcx
    dec rbx
    add dl, '0'
    mov [rbx], dl
    inc r13
    test rax, rax
    jnz .loop
    mov rsi, rbx
    mov rdx, r13
.write:
    mov rax, 1
    mov rdi, r8
    syscall
    ret
"""
APLUS_FILE["nasm216"] = _NASM_FILE

assert set(APLUS_FILE) == set(APLUS), (
    f"key mismatch stdio={set(APLUS)-set(APLUS_FILE)} file={set(APLUS_FILE)-set(APLUS)}"
)

/** A+B namunalari — `/about` yo'riqnomasi.
 *
 * Manba: `tools/aplus_solutions.py`, `tools/aplus_file_solutions.py`.
 * Yangilash: `python tools/render_language_samples.py`
 */
export const LANGUAGE_SAMPLES: Record<string, string> = {
  "ada14": `with Ada.Long_Long_Integer_Text_IO;

procedure Main is
   A, B : Long_Long_Integer;
begin
   Ada.Long_Long_Integer_Text_IO.Get (A);
   Ada.Long_Long_Integer_Text_IO.Get (B);
   Ada.Long_Long_Integer_Text_IO.Put (A + B, Width => 0);
end Main;
`,
  "c17": `#include <stdio.h>

int main(void) {
    long long a, b;
    if (scanf("%lld %lld", &a, &b) != 2) return 0;
    printf("%lld", a + b);
    return 0;
}
`,
  "caml53": `let () =
  Scanf.scanf "%Ld %Ld" (fun a b -> Printf.printf "%Ld" (Int64.add a b))
`,
  "cobol32": `       IDENTIFICATION DIVISION.
       PROGRAM-ID. MAIN.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-LINE PIC X(128).
       01 A PIC S9(18) COMP-5.
       01 B PIC S9(18) COMP-5.
       01 WS-TOTAL PIC S9(18) COMP-5.
       01 WS-OUT PIC -Z(18)9.
       01 WS-RAW PIC X(21).
       01 WS-DIS PIC X(24).
       01 WS-IDX PIC 9(2) VALUE 1.
       01 WS-LEN PIC 9(2) VALUE 0.
       PROCEDURE DIVISION.
           ACCEPT WS-LINE
           UNSTRING WS-LINE DELIMITED BY ALL SPACE
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
           DISPLAY WS-DIS(1:WS-LEN) WITH NO ADVANCING
           STOP RUN.
`,
  "cpp23": `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long a, b;
    if (!(cin >> a >> b)) return 0;
    cout << a + b;
    return 0;
}
`,
  "csharp14": `using System;

class Program {
    static void Main() {
        var parts = Console.ReadLine()!.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        Console.Write(long.Parse(parts[0]) + long.Parse(parts[1]));
    }
}
`,
  "d140": `import std.stdio;

void main() {
    long a, b;
    if (readf("%d %d", &a, &b) != 2) return;
    write(a + b);
}
`,
  "dart313": `import 'dart:io';

void main() {
  final parts = stdin.readLineSync()!.split(RegExp(r'\s+'));
  stdout.write(int.parse(parts[0]) + int.parse(parts[1]));
}
`,
  "fortran14": `program main
  implicit none
  integer(8) :: a, b
  read *, a, b
  write(*, '(I0)', advance='no') a + b
end program main
`,
  "fsharp10": `[<EntryPoint>]
let main _ =
    let parts = System.Console.ReadLine().Split(' ')
    System.Console.Write(int64 parts.[0] + int64 parts.[1])
    0
`,
  "go124": `package main

import "fmt"

func main() {
    var a, b int64
    if _, err := fmt.Scan(&a, &b); err != nil {
        return
    }
    fmt.Print(a + b)
}
`,
  "haskell96": `main = do
  line <- getLine
  let [sa, sb] = words line
  putStr (show (read sa + read sb :: Integer))
`,
  "java21": `import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        var br = new BufferedReader(new InputStreamReader(System.in));
        var st = new StringTokenizer(br.readLine());
        long a = Long.parseLong(st.nextToken());
        long b = Long.parseLong(st.nextToken());
        System.out.print(a + b);
    }
}
`,
  "js24": `const fs = require("fs");
const input = fs.readFileSync(0, "utf8").trim().split(/\s+/);
if (input.length >= 2) {
  process.stdout.write(String(Number(input[0]) + Number(input[1])));
}
`,
  "julia113": `function solve()
    s = readline()
    sp = findfirst(' ', s)
    a = parse(Int64, s[1:sp - 1])
    b = parse(Int64, s[sp + 1:end])
    print(a + b)
end
solve()
`,
  "kotlin24": `fun main() {
    val (a, b) = readln().split(" ").map { it.toLong() }
    print(a + b)
}
`,
  "lisp25": `(princ (+ (read) (read)))
`,
  "lua54": `local line = io.read("*l")
local a, b = line:match("(%S+)%s+(%S+)")
io.write(tonumber(a) + tonumber(b))
`,
  "nasm216": `default rel
section .bss
inbuf: resb 64
outbuf: resb 32

section .text
global _start

_start:
    mov rax, 0
    mov rdi, 0
    mov rsi, inbuf
    mov rdx, 64
    syscall
    mov rdi, inbuf
    call parse_int
    mov r12, rax
    call skip_sep
    call parse_int
    add rax, r12
    call print_int
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
    mov rdi, 1
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
    mov rdi, 1
    syscall
    ret
`,
  "objc14": `#import <stdio.h>

int main(void) {
    long long a, b;
    if (scanf("%lld %lld", &a, &b) != 2) return 0;
    printf("%lld", a + b);
    return 0;
}
`,
  "ocaml53": `let () =
  Scanf.scanf "%Ld %Ld" (fun a b -> Printf.printf "%Ld" (Int64.add a b))
`,
  "pascal322": `program Main;
var a, b: int64;
begin
  readln(a, b);
  write(a + b);
end.
`,
  "perl540": `my $line = <STDIN>;
chomp $line;
my ($a, $b) = split ' ', $line;
print $a + $b;
`,
  "php84": `<?php
$in = trim(fgets(STDIN));
if ($in === '') { exit(0); }
$parts = preg_split('/\s+/', $in);
echo (int)$parts[0] + (int)$parts[1];
`,
  "powershell76": `$line = [Console]::In.ReadLine()
$parts = $line.Split(' ', [StringSplitOptions]::RemoveEmptyEntries)
[Console]::Write([int64]$parts[0] + [int64]$parts[1])
`,
  "prolog92": `:- initialization(main, main).

main :-
    read_line_to_string(user_input, Line),
    split_string(Line, " ", " \t", Parts),
    maplist(number_string, [A, B], Parts),
    Sum is A + B,
    format('~w', [Sum]).
`,
  "py313": `import sys

data = sys.stdin.read().split()
if len(data) >= 2:
    print(int(data[0]) + int(data[1]), end="")
`,
  "pypy73": `import sys

data = sys.stdin.read().split()
if len(data) >= 2:
    print(int(data[0]) + int(data[1]), end="")
`,
  "r45": `x <- read.table(file("stdin"), nrows=1)
cat(x[1, 1] + x[1, 2], sep="")
`,
  "ruby33": `a, b = gets.to_s.split.map(&:to_i)
print(a + b)
`,
  "rust185": `use std::io::{self, Read};

fn main() {
    let mut s = String::new();
    io::stdin().read_to_string(&mut s).unwrap();
    let mut it = s.split_whitespace();
    let a: i64 = it.next().unwrap().parse().unwrap();
    let b: i64 = it.next().unwrap().parse().unwrap();
    print!("{}", a + b);
}
`,
  "scala39": `object Main {
  def main(args: Array[String]): Unit = {
    val p = scala.io.StdIn.readLine().split(" ")
    print(p(0).toLong + p(1).toLong)
  }
}
`,
  "swift60": `import Foundation
let parts = readLine()!.split(separator: " ")
let a = Int(parts[0])!
let b = Int(parts[1])!
print(a + b, terminator: "")
`,
  "ts24": `const fs = require("fs");
const input = fs.readFileSync(0, "utf8").trim().split(/\s+/);
if (input.length >= 2) {
  process.stdout.write(String(Number(input[0]) + Number(input[1])));
}
`,
  "vbnet17": `Imports System

Module Program
    Sub Main()
        Dim parts = Console.ReadLine().Split(" "c, StringSplitOptions.RemoveEmptyEntries)
        Console.Write(Long.Parse(parts(0)) + Long.Parse(parts(1)))
    End Sub
End Module
`
};

export const LANGUAGE_FILE_SAMPLES: Record<string, string> = {
  "ada14": `with Ada.Text_IO;
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
`,
  "c17": `#include <stdio.h>

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
`,
  "caml53": `let () =
  let ic = open_in "input.txt" in
  let line = input_line ic in
  close_in ic;
  Scanf.sscanf line "%Ld %Ld" (fun a b ->
    let oc = open_out "output.txt" in
    Printf.fprintf oc "%Ld" (Int64.add a b);
    close_out oc)
`,
  "cobol32": `       IDENTIFICATION DIVISION.
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
`,
  "cpp23": `#include <bits/stdc++.h>
using namespace std;

int main() {
    ifstream in("input.txt");
    ofstream out("output.txt");
    long long a, b;
    if (!(in >> a >> b)) return 0;
    out << a + b;
    return 0;
}
`,
  "csharp14": `using System.IO;

class Program {
    static void Main() {
        var line = File.ReadAllText("input.txt").Trim();
        var sp = line.IndexOf(' ');
        var a = long.Parse(line.Substring(0, sp));
        var b = long.Parse(line.Substring(sp + 1).Trim());
        File.WriteAllText("output.txt", (a + b).ToString());
    }
}
`,
  "d140": `import std.array;
import std.conv;
import std.format;
import std.file;

void main() {
    auto parts = readText("input.txt").split();
    long a = to!long(parts[0]);
    long b = to!long(parts[1]);
    write("output.txt", format("%s", a + b));
}
`,
  "dart313": `import 'dart:io';

void main() {
  final parts = File('input.txt').readAsStringSync().trim().split(RegExp(r'\s+'));
  File('output.txt').writeAsStringSync('\${int.parse(parts[0]) + int.parse(parts[1])}');
}
`,
  "fortran14": `program main
  implicit none
  integer(8) :: a, b
  open(10, file='input.txt', status='old')
  read(10, *) a, b
  close(10)
  open(11, file='output.txt', status='replace')
  write(11, '(I0)', advance='no') a + b
  close(11)
end program main
`,
  "fsharp10": `[<EntryPoint>]
let main _ =
    let parts = System.IO.File.ReadAllText("input.txt").Trim().Split(' ')
    System.IO.File.WriteAllText("output.txt", string (int64 parts.[0] + int64 parts.[1]))
    0
`,
  "go124": `package main

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
`,
  "haskell96": `main = do
  line <- readFile "input.txt"
  let [sa, sb] = words line
  writeFile "output.txt" (show (read sa + read sb :: Integer))
`,
  "java21": `import java.io.*;
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
`,
  "js24": `const fs = require("fs");
const input = fs.readFileSync("input.txt", "utf8").trim().split(/\s+/);
if (input.length >= 2) {
  fs.writeFileSync("output.txt", String(Number(input[0]) + Number(input[1])));
}
`,
  "julia113": `function solve()
    s = read("input.txt", String)
    sp = findfirst(' ', s)
    a = parse(Int64, s[1:sp - 1])
    b = parse(Int64, s[sp + 1:end])
    open("output.txt", "w") do io
        print(io, a + b)
    end
end
solve()
`,
  "kotlin24": `fun main() {
    val parts = java.io.File("input.txt").readText().trim().split(" ")
    val sum = parts[0].toLong() + parts[1].toLong()
    java.io.File("output.txt").writeText(sum.toString())
}
`,
  "lisp25": `(with-open-file (in "input.txt" :direction :input)
  (let* ((a (read in))
         (b (read in)))
    (with-open-file (out "output.txt" :direction :output :if-exists :supersede)
      (princ (+ a b) out))))
`,
  "lua54": `local f = io.open("input.txt", "r")
local line = f:read("*l")
f:close()
local a, b = line:match("(%S+)%s+(%S+)")
local out = io.open("output.txt", "w")
out:write(tonumber(a) + tonumber(b))
out:close()
`,
  "nasm216": `default rel
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
    mov r8, 1
    mov rax, r13
    call print_int
    mov rax, 60
    xor rdi, rdi
    syscall

skip_sep:
.s:
    mov al, [rdi]
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
    mov rax, 1
    mov rdi, r8
    syscall
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
`,
  "objc14": `#import <stdio.h>

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
`,
  "ocaml53": `let () =
  let ic = open_in "input.txt" in
  let line = input_line ic in
  close_in ic;
  Scanf.sscanf line "%Ld %Ld" (fun a b ->
    let oc = open_out "output.txt" in
    Printf.fprintf oc "%Ld" (Int64.add a b);
    close_out oc)
`,
  "pascal322": `program Main;
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
`,
  "perl540": `open my $in, '<', 'input.txt' or exit 1;
my $line = <$in>;
close $in;
chomp $line;
my ($a, $b) = split ' ', $line;
open my $out, '>', 'output.txt' or exit 1;
print $out $a + $b;
close $out;
`,
  "php84": `<?php
$in = trim(file_get_contents("input.txt"));
if ($in === '') { exit(0); }
$parts = preg_split('/\s+/', $in);
file_put_contents("output.txt", (string)((int)$parts[0] + (int)$parts[1]));
`,
  "powershell76": `$line = Get-Content -Path "input.txt" -TotalCount 1
$parts = $line.Split(' ', [StringSplitOptions]::RemoveEmptyEntries)
Set-Content -Path "output.txt" -Value ([int64]$parts[0] + [int64]$parts[1]) -NoNewline
`,
  "prolog92": `:- initialization(main, main).

main :-
    setup_call_cleanup(
        open('input.txt', read, In, []),
        ( read_line_to_string(In, Line),
          split_string(Line, " ", " \t", Parts),
          maplist(number_string, [A, B], Parts),
          Sum is A + B,
          setup_call_cleanup(
              open('output.txt', write, Out, []),
              format(Out, '~w', [Sum]),
              close(Out))
        ),
        close(In)).
`,
  "py313": `from pathlib import Path

data = Path("input.txt").read_text().split()
if len(data) >= 2:
    Path("output.txt").write_text(str(int(data[0]) + int(data[1])))
`,
  "pypy73": `from pathlib import Path

data = Path("input.txt").read_text().split()
if len(data) >= 2:
    Path("output.txt").write_text(str(int(data[0]) + int(data[1])))
`,
  "r45": `x <- read.table("input.txt", nrows = 1)
cat(as.integer(x[1, 1] + x[1, 2]), file = "output.txt")
`,
  "ruby33": `line = File.read("input.txt")
a, b = line.split.map(&:to_i)
File.write("output.txt", (a + b).to_s)
`,
  "rust185": `use std::fs;

fn main() {
    let s = fs::read_to_string("input.txt").unwrap();
    let mut it = s.split_whitespace();
    let a: i64 = it.next().unwrap().parse().unwrap();
    let b: i64 = it.next().unwrap().parse().unwrap();
    fs::write("output.txt", format!("{}", a + b)).unwrap();
}
`,
  "scala39": `object Main {
  def main(args: Array[String]): Unit = {
    val p = scala.io.Source.fromFile("input.txt").getLines().next().split(" ")
    val out = new java.io.PrintWriter("output.txt")
    out.print(p(0).toLong + p(1).toLong)
    out.close()
  }
}
`,
  "swift60": `import Glibc
let inp = fopen("input.txt", "r")
var a: Int64 = 0
var b: Int64 = 0
_ = fscanf(inp, "%lld %lld", &a, &b)
fclose(inp)
let out = fopen("output.txt", "w")
fprintf(out, "%lld", a + b)
fclose(out)
`,
  "ts24": `const fs = require("fs");
const input = fs.readFileSync("input.txt", "utf8").trim().split(/\s+/);
if (input.length >= 2) {
  fs.writeFileSync("output.txt", String(Number(input[0]) + Number(input[1])));
}
`,
  "vbnet17": `Imports System.IO

Module Program
    Sub Main()
        Dim line = File.ReadAllText("input.txt").Trim()
        Dim sp = line.IndexOf(" "c)
        Dim a = Long.Parse(line.Substring(0, sp))
        Dim b = Long.Parse(line.Substring(sp + 1).Trim())
        File.WriteAllText("output.txt", (a + b).ToString())
    End Sub
End Module
`
};

/** Monaco til identifikatori — faqat ko'rinish uchun. */
export function sampleEditorLanguage(code: string): string {
  if (code.startsWith("cpp") || code === "c17") return "cpp";
  if (code.startsWith("py") || code === "pypy73") return "python";
  if (code.startsWith("java") || code.startsWith("kotlin") || code.startsWith("scala"))
    return "java";
  if (code === "js24" || code === "ts24") return "javascript";
  if (code === "csharp14" || code === "fsharp10" || code === "vbnet17") return "csharp";
  if (code === "go124") return "go";
  if (code.startsWith("rust")) return "rust";
  if (code === "php84") return "php";
  if (code === "ruby33") return "ruby";
  if (code === "pascal322") return "pascal";
  if (code === "swift60") return "swift";
  if (code === "dart313") return "dart";
  return "plaintext";
}

export function sampleForLanguage(code: string): string | null {
  return LANGUAGE_SAMPLES[code] ?? null;
}

export function sampleFileForLanguage(code: string): string | null {
  return LANGUAGE_FILE_SAMPLES[code] ?? null;
}

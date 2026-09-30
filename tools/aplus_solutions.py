"""Canonical A+B solutions for all judge languages (verified on `a-plus-b`).

Synced to `apps/web/src/content/about/language-samples.ts` via
`tools/render_language_samples.py`.
"""

from __future__ import annotations

APLUS: dict[str, str] = {
    "cpp23": """#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    long long a, b;
    if (!(cin >> a >> b)) return 0;
    cout << a + b;
    return 0;
}
""",
    "c17": """#include <stdio.h>

int main(void) {
    long long a, b;
    if (scanf("%lld %lld", &a, &b) != 2) return 0;
    printf("%lld", a + b);
    return 0;
}
""",
    "py313": """import sys

data = sys.stdin.read().split()
if len(data) >= 2:
    print(int(data[0]) + int(data[1]), end="")
""",
    "pypy73": """import sys

data = sys.stdin.read().split()
if len(data) >= 2:
    print(int(data[0]) + int(data[1]), end="")
""",
    "java21": """import java.io.*;
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
""",
    "js24": """const fs = require("fs");
const input = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
if (input.length >= 2) {
  process.stdout.write(String(Number(input[0]) + Number(input[1])));
}
""",
    "ts24": """const fs = require("fs");
const input = fs.readFileSync(0, "utf8").trim().split(/\\s+/);
if (input.length >= 2) {
  process.stdout.write(String(Number(input[0]) + Number(input[1])));
}
""",
    "csharp14": """using System;

class Program {
    static void Main() {
        var parts = Console.ReadLine()!.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        Console.Write(long.Parse(parts[0]) + long.Parse(parts[1]));
    }
}
""",
    "go124": """package main

import "fmt"

func main() {
    var a, b int64
    if _, err := fmt.Scan(&a, &b); err != nil {
        return
    }
    fmt.Print(a + b)
}
""",
    "rust185": """use std::io::{self, Read};

fn main() {
    let mut s = String::new();
    io::stdin().read_to_string(&mut s).unwrap();
    let mut it = s.split_whitespace();
    let a: i64 = it.next().unwrap().parse().unwrap();
    let b: i64 = it.next().unwrap().parse().unwrap();
    print!("{}", a + b);
}
""",
    "kotlin24": """fun main() {
    val (a, b) = readln().split(" ").map { it.toLong() }
    print(a + b)
}
""",
    "php84": """<?php
$in = trim(fgets(STDIN));
if ($in === '') { exit(0); }
$parts = preg_split('/\\s+/', $in);
echo (int)$parts[0] + (int)$parts[1];
""",
    "ruby33": """a, b = gets.to_s.split.map(&:to_i)
print(a + b)
""",
    "pascal322": """program Main;
var a, b: int64;
begin
  readln(a, b);
  write(a + b);
end.
""",
    "swift60": """import Foundation
let parts = readLine()!.split(separator: " ")
let a = Int(parts[0])!
let b = Int(parts[1])!
print(a + b, terminator: "")
""",
    "dart313": """import 'dart:io';

void main() {
  final parts = stdin.readLineSync()!.split(RegExp(r'\\s+'));
  stdout.write(int.parse(parts[0]) + int.parse(parts[1]));
}
""",
    "haskell96": """main = do
  line <- getLine
  let [sa, sb] = words line
  putStr (show (read sa + read sb :: Integer))
""",
    "r45": """x <- read.table(file("stdin"), nrows=1)
cat(x[1, 1] + x[1, 2], sep="")
""",
    "perl540": """my $line = <STDIN>;
chomp $line;
my ($a, $b) = split ' ', $line;
print $a + $b;
""",
    "d140": """import std.stdio;

void main() {
    long a, b;
    if (readf("%d %d", &a, &b) != 2) return;
    write(a + b);
}
""",
    "ocaml53": """let () =
  Scanf.scanf "%Ld %Ld" (fun a b -> Printf.printf "%Ld" (Int64.add a b))
""",
    "caml53": """let () =
  Scanf.scanf "%Ld %Ld" (fun a b -> Printf.printf "%Ld" (Int64.add a b))
""",
    "scala39": """object Main {
  def main(args: Array[String]): Unit = {
    val p = scala.io.StdIn.readLine().split(" ")
    print(p(0).toLong + p(1).toLong)
  }
}
""",
    "vbnet17": """Imports System

Module Program
    Sub Main()
        Dim parts = Console.ReadLine().Split(" "c, StringSplitOptions.RemoveEmptyEntries)
        Console.Write(Long.Parse(parts(0)) + Long.Parse(parts(1)))
    End Sub
End Module
""",
    "fortran14": """program main
  implicit none
  integer(8) :: a, b
  read *, a, b
  write(*, '(I0)', advance='no') a + b
end program main
""",
    "ada14": """with Ada.Long_Long_Integer_Text_IO;

procedure Main is
   A, B : Long_Long_Integer;
begin
   Ada.Long_Long_Integer_Text_IO.Get (A);
   Ada.Long_Long_Integer_Text_IO.Get (B);
   Ada.Long_Long_Integer_Text_IO.Put (A + B, Width => 0);
end Main;
""",
    "objc14": """#import <stdio.h>

int main(void) {
    long long a, b;
    if (scanf("%lld %lld", &a, &b) != 2) return 0;
    printf("%lld", a + b);
    return 0;
}
""",
    "cobol32": """       IDENTIFICATION DIVISION.
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
""",
    "julia113": """a, b = parse.(Int64, split(readline()))
print(a + b)
""",
    "prolog92": """:- initialization(main, main).

main :-
    read_line_to_string(user_input, Line),
    split_string(Line, " ", " \\t", Parts),
    maplist(number_string, [A, B], Parts),
    Sum is A + B,
    format('~w', [Sum]).
""",
    "lua54": """local line = io.read("*l")
local a, b = line:match("(%S+)%s+(%S+)")
io.write(tonumber(a) + tonumber(b))
""",
    "powershell76": """$line = [Console]::In.ReadLine()
$parts = $line.Split(' ', [StringSplitOptions]::RemoveEmptyEntries)
[Console]::Write([int64]$parts[0] + [int64]$parts[1])
""",
    "lisp25": """(princ (+ (read) (read)))
""",
    "fsharp10": """[<EntryPoint>]
let main _ =
    let parts = System.Console.ReadLine().Split(' ')
    System.Console.Write(int64 parts.[0] + int64 parts.[1])
    0
""",
    "nasm216": """default rel
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
""",
}

import subprocess
import tempfile
import os
import re
from typing import Tuple, Optional


# LANGUAGE REGISTRY
# Every supported language is defined here — one entry per language.
# To add a new language, just add a new dict to this list.

LANGUAGE_REGISTRY = [
    {
        "name": "python",
        "extensions":[".py"],
        "run_cmd":["python", "{file}"],
        "syntax_cmd": ["python", "-m", "py_compile", "{file}"],
        "server_keywords":[
            "app.run(", "flask", "fastapi", "uvicorn", "django",
            "socketio", "tornado", "aiohttp", "starlette",
            "streamlit", "gradio", "panel", "dash",
        ],
        "detect_keywords":[
            "def ", "import ", "print(", "if __name__", "class ",
            "elif ", "lambda ", "async def", "await ",
        ],
        "shebang":None,
    },

    {
        "name":"javascript",
        "extensions": [".js"],
        "run_cmd": ["node", "{file}"],
        "syntax_cmd": ["node", "--check", "{file}"],
        "server_keywords": [
            "express()", "app.listen(", "http.createserver",
            "https.createserver", "fastify(", "koa(", "hapi",
            "socket.io", "ws.server",
        ],
        "detect_keywords": [
            "const ", "let ", "var ", "function ", "console.log",
            "require(", "module.exports", "=>", "async ", "await ",
            "document.", "window.", "process.",
        ],
        "shebang": "#!/usr/bin/env node",
    },

    # TypeScript 
    {
        "name": "typescript",
        "extensions": [".ts"],
        "run_cmd": ["npx", "ts-node", "{file}"],
        "syntax_cmd": ["npx", "tsc", "--noEmit", "--allowJs", "{file}"],
        "server_keywords": [
            "express()", "app.listen(", "nestfactory", "fastify(",
        ],
        "detect_keywords": [
            ": string", ": number", ": boolean", "interface ",
            "type ", "<T>", "enum ", ": void", "as string", "as number",
        ],
        "shebang": None,
    },

    {
        "name": "java",
        "extensions": [".java"],
        "run_cmd": None,   
        "syntax_cmd": ["javac", "{file}"],
        "server_keywords": [
            "springapplication.run", "@springbootapplication",
            "tomcat", "jetty", "undertow", "server.start",
        ],
        "detect_keywords": [
            "public class ", "public static void main",
            "system.out.println", "import java.", "private ", "protected ",
            "@override", "extends ", "implements ",
        ],
        "shebang": None,
        "compile_run": True,   
    },

    {
        "name": "c",
        "extensions": [".c"],
        "run_cmd": None,   
        "syntax_cmd": ["gcc", "-fsyntax-only", "{file}"],
        "server_keywords": [
            "bind(", "listen(", "accept(", "socket(",
        ],
        "detect_keywords": [
            "#include ", "int main(", "printf(", "scanf(",
            "malloc(", "free(", "struct ", "typedef ",
        ],
        "shebang": None,
        "compile_run": True,
        "compile_cmd": ["gcc", "{file}", "-o", "{binary}"],
    },

    {
        "name": "cpp",
        "extensions": [".cpp", ".cc", ".cxx"],
        "run_cmd": None,
        "syntax_cmd": ["g++", "-fsyntax-only", "{file}"],
        "server_keywords": [
            "boost::asio", "asio::", "crow::", "pistache::",
        ],
        "detect_keywords": [
            "#include <iostream>", "std::", "cout <<", "cin >>",
            "int main(", "namespace ", "template<", "vector<",
            "nullptr", "auto ",
        ],
        "shebang": None,
        "compile_run": True,
        "compile_cmd": ["g++", "{file}", "-o", "{binary}"],
    },

    {
        "name": "csharp",
        "extensions": [".cs"],
        "run_cmd": ["dotnet", "script", "{file}"],
        "syntax_cmd": ["dotnet", "build"],
        "server_keywords": [
            "webapplication.createbuilder", "app.run()",
            "ihostbuilder", "iwebhostbuilder", "aspnetcore",
        ],
        "detect_keywords": [
            "using system", "namespace ", "public class ",
            "console.writeline", "static void main", "async task",
            "var ", "string[] args",
        ],
        "shebang": None,
    },

    {
        "name": "go",
        "extensions": [".go"],
        "run_cmd": ["go", "run", "{file}"],
        "syntax_cmd": ["go", "vet", "{file}"],
        "server_keywords": [
            "http.listenandserve", "http.listenandservetls",
            "gin.default()", "echo.new()", "fiber.new(",
        ],
        "detect_keywords": [
            "package main", "func main()", "fmt.println",
            "import (", ":= ", "var ", "func ", "go func",
            "chan ", "defer ", "goroutine",
        ],
        "shebang": None,
    },

    {
        "name": "rust",
        "extensions": [".rs"],
        "run_cmd": ["rustc", "{file}", "-o", "{binary}"],
        "syntax_cmd": ["rustc", "--edition", "2021", "--emit=metadata", "-o", "/dev/null", "{file}"],
        "server_keywords": [
            "actix_web", "rocket::", "warp::", "axum::",
            "hyper::server", "tokio::main",
        ],
        "detect_keywords": [
            "fn main()", "let mut ", "println!(", "use std::",
            "struct ", "impl ", "enum ", "match ", "vec![",
            "unwrap()", "expect(", "pub fn",
        ],
        "shebang": None,
        "compile_run": True,
        "compile_cmd": ["rustc", "{file}", "-o", "{binary}"],
    },

    {
        "name": "php",
        "extensions": [".php"],
        "run_cmd": ["php", "{file}"],
        "syntax_cmd": ["php", "-l", "{file}"],
        "server_keywords": [
            "laravel", "symfony", "slim\\", "echo new server",
        ],
        "detect_keywords": [
            "<?php", "echo ", "$_get", "$_post", "$_session",
            "function ", "class ", "->", "namespace ",
        ],
        "shebang": None,
    },

    {
        "name": "ruby",
        "extensions": [".rb"],
        "run_cmd": ["ruby", "{file}"],
        "syntax_cmd": ["ruby", "-c", "{file}"],
        "server_keywords": [
            "rails", "sinatra", "rack::", "puma", "unicorn",
            "run lambdas", "rack::handler",
        ],
        "detect_keywords": [
            "def ", "end", "puts ", "require ", "class ",
            "attr_", "do |", "each do", "| do",
        ],
        "shebang": "#!/usr/bin/env ruby",
    },

    {
        "name": "kotlin",
        "extensions": [".kt"],
        "run_cmd": ["kotlinc", "-script", "{file}"],
        "syntax_cmd": ["kotlinc", "{file}", "-include-runtime", "-d", "/tmp/out.jar"],
        "server_keywords": [
            "embeddedserver(", "ktor", "spring",
        ],
        "detect_keywords": [
            "fun main(", "val ", "var ", "println(", "data class ",
            "object ", "companion object", "suspend fun", "coroutine",
        ],
        "shebang": None,
    },

    {
        "name": "swift",
        "extensions": [".swift"],
        "run_cmd": ["swift", "{file}"],
        "syntax_cmd": ["swiftc", "-typecheck", "{file}"],
        "server_keywords": [
            "vapor", "kitura", "perfect.", "hummingbird",
        ],
        "detect_keywords": [
            "import swift", "var ", "let ", "func ", "print(",
            "class ", "struct ", "enum ", "guard ", "if let ",
        ],
        "shebang": None,
    },

    {
        "name": "bash",
        "extensions": [".sh", ".bash"],
        "run_cmd": ["bash", "{file}"],
        "syntax_cmd": ["bash", "-n", "{file}"],
        "detect_keywords": [
            "#!/bin/bash", "#!/bin/sh", "echo ", "if [", "fi",
            "for ", "do\n", "done", "export ", "source ",
        ],
        "shebang": "#!/bin/bash",
    },

    {
        "name": "r",
        "extensions": [".r"],
        "run_cmd": ["Rscript", "{file}"],
        "syntax_cmd": ["Rscript", "--vanilla", "-e", "parse(file='{file}')"],
        "server_keywords": [
            "shiny::runapp", "plumber", "httpuv",
        ],
        "detect_keywords": [
            "<- ", "library(", "require(", "data.frame(",
            "ggplot(", "print(", "cat(", "function(",
        ],
        "shebang": None,
    },

    {
        "name": "scala",
        "extensions": [".scala"],
        "run_cmd": ["scala", "{file}"],
        "syntax_cmd": ["scalac", "{file}"],
        "server_keywords": [
            "akka.http", "play.api", "http4s", "zio-http",
        ],
        "detect_keywords": [
            "object ", "def main", "println(", "val ", "var ",
            "case class", "trait ", "extends ", "implicit ",
        ],
        "shebang": None,
    },

    {
        "name":             "perl",
        "extensions":       [".pl", ".pm"],
        "run_cmd":          ["perl", "{file}"],
        "syntax_cmd":       ["perl", "-c", "{file}"],
        "server_keywords":  [
            "mojolicious", "catalyst", "dancer", "plack",
        ],
        "detect_keywords":  [
            "#!/usr/bin/perl", "use strict", "use warnings",
            "my $", "print ", "sub ", "foreach ", "@_",
        ],
        "shebang": "#!/usr/bin/perl",
    },


# DETECTION

def _strip_fences(code: str) -> Tuple[str, Optional[str]]:
    """
    Strips markdown fences and returns (clean_code, detected_lang_hint).
    """
    match = re.search(r"```(\w+)?\n(.*?)```", code, re.DOTALL)
    if match:
        lang_hint = match.group(1)           
        clean     = match.group(2).strip()
        return clean, lang_hint
    return code.strip(), None


def _detect_language(code: str, hint: Optional[str], state_language: str) -> dict:
    """
    Returns the language registry entry for the detected language.
    Priority: 1) state['language']  2) fence hint  3) keyword scoring
    Falls back to Python if nothing matches.
    """
    # explicit language set in state 
    if state_language:
        lang = state_language.lower().strip()
        for entry in LANGUAGE_REGISTRY:
            if lang == entry["name"] or lang in [e.lstrip(".") for e in entry["extensions"]]:
                return entry

    # fence hint  
    if hint:
        hint_lower = hint.lower()
        for entry in LANGUAGE_REGISTRY:
            if hint_lower == entry["name"] or hint_lower in [e.lstrip(".") for e in entry["extensions"]]:
                return entry

    # keyword scoring
    lower_code = code.lower()
    scores = {}
    for entry in LANGUAGE_REGISTRY:
        score = sum(1 for kw in entry["detect_keywords"] if kw.lower() in lower_code)
        if score > 0:
            scores[entry["name"]] = score

    if scores:
        best = max(scores, key=scores.get)
        for entry in LANGUAGE_REGISTRY:
            if entry["name"] == best:
                print(f"Language detected by keyword scoring: {best} (score={scores[best]})")
                return entry

    #  fallback
    print("Could not detect language — defaulting to Python.")
    return LANGUAGE_REGISTRY[0]


def _is_server_code(code: str, lang_entry: dict) -> bool:
    lower = code.lower()
    return any(kw in lower for kw in lang_entry.get("server_keywords", []))


# EXECUTION STRATEGIES

def _run_command(cmd: list, timeout: int = 10) -> Tuple[bool, str, str]:
    """Runs a command. Returns (success, stdout, stderr)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Timed out after {timeout}s"
    except FileNotFoundError as e:
        return False, "", f"Runtime not found: {e}"
    except Exception as e:
        return False, "", str(e)


def _write_temp(code: str, suffix: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="w") as f:
        f.write(code)
        return f.name


def _fill(template: list, file: str, binary: str = "") -> list:
    """Fills {file} and {binary} placeholders in a command template."""
    return [p.replace("{file}", file).replace("{binary}", binary) for p in template]


def _syntax_check_only(code: str, lang: dict) -> Tuple[bool, str]:
    """Runs syntax/compile check only — never executes."""
    suffix = lang["extensions"][0]
    tmp    = _write_temp(code, suffix)
    cmd    = _fill(lang["syntax_cmd"], tmp)
    ok, out, err = _run_command(cmd)
    os.unlink(tmp)
    return ok, err or out


def _full_execute(code: str, lang: dict) -> Tuple[bool, str]:
    """
    Runs the code fully.
    Handles three cases:
      - compile_run=True with compile_cmd  (C, C++, Rust, Java)
      - plain run_cmd  (Python, Node, Ruby, PHP …)
      - syntax_cmd fallback if run_cmd is None
    """
    suffix = lang["extensions"][0]
    tmp    = _write_temp(code, suffix)

    #compiled languages 
    if lang.get("compile_run") and lang.get("compile_cmd"):
        binary = tmp.replace(suffix, "")
        compile_cmd = _fill(lang["compile_cmd"], tmp, binary)
        ok, out, err = _run_command(compile_cmd, timeout=30)
        if not ok:
            os.unlink(tmp)
            return False, f"Compile Error:\n{err}"
        # run the binary
        ok, out, err = _run_command([binary])
        os.unlink(tmp)
        try:
            os.unlink(binary)
        except Exception:
            pass
        if ok:
            return True, out
        return False, f"Runtime Error:\n{err}"

    #  interpreted languages 
    if lang.get("run_cmd"):
        cmd = _fill(lang["run_cmd"], tmp)
        ok, out, err = _run_command(cmd)
        os.unlink(tmp)
        if ok:
            return True, out
        return False, f"Execution Error:\n{err}"

    #  fallback: syntax check only 
    ok, err = _syntax_check_only(code, lang)
    os.unlink(tmp)
    return ok, err


# FAILURE HANDLER

def _handle_failure(error_msg: str, fix_attempts: int, max_attempts: int, iteration: int) -> dict:
    if fix_attempts >= max_attempts:
        print(f"Max fix attempts ({max_attempts}) reached. Forwarding to explainer.")
        return {
            "analysis":         f"Could not fix after {max_attempts} attempts.\n{error_msg}",
            "tool_result":      error_msg,
            "execution_status": "failed",
            "fix_attempts":     0,
            "next_agent":       "explainer_agent",
        }
    return {
        "analysis":         error_msg,
        "tool_result":      error_msg,
        "execution_status": "failed",
        "iteration":        iteration + 1,
        "fix_attempts":     fix_attempts + 1,
        "next_agent":       "fix_agent",
    }


# MAIN AGENT

def execution_agent(state):
    print("Running Execution Agent...")

    code          = state.get("fixed_code") or state.get("code", "")
    iteration     = state.get("iteration", 0)
    fix_attempts  = state.get("fix_attempts", 0)
    max_attempts  = state.get("max_fix_attempts", 3)
    state_lang    = state.get("language", "")

    if not code or not code.strip():
        return {
            "analysis":         "No code to execute.",
            "execution_status": "failed",
            "next_agent":       "explainer_agent",
        }

    clean_code, fence_hint = _strip_fences(code)
    lang = _detect_language(clean_code, fence_hint, state_lang)
    print(f"Language: {lang['name']}")

    if _is_server_code(clean_code, lang):
        print(f"Server/framework code detected ({lang['name']}) — syntax check only.")
        ok, error = _syntax_check_only(clean_code, lang)
        if ok:
            return {
                "analysis":         f"Syntax check passed ({lang['name']} server code — not executed).",
                "execution_status": "success",
                "fix_attempts":     0,
                "language":         lang["name"],
                "next_agent":       "explainer_agent",
            }
        return _handle_failure(f"Syntax Error ({lang['name']}):\n{error}",
                               fix_attempts, max_attempts, iteration)

    print(f"Executing {lang['name']} code...")
    ok, output = _full_execute(clean_code, lang)

    if ok:
        print(f"Execution succeeded ({lang['name']}).")
        return {
            "analysis":         f"Execution Success ({lang['name']}):\n{output}",
            "execution_status": "success",
            "fix_attempts":     0,
            "language":         lang["name"],
            "next_agent":       "explainer_agent",
        }

    print(f"Execution failed (attempt {fix_attempts + 1}/{max_attempts}) [{lang['name']}]:\n{output}")
    return _handle_failure(output, fix_attempts, max_attempts, iteration)

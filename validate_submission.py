# -*- coding: utf-8 -*-
"""
============================================================
 Submission Validator - AI Learning Assistant on Telegram
============================================================
 Validates all 10 core requirements for the Partnr submission.
 Run: python validate_submission.py
============================================================
"""

import os
import sys
import re

# Force UTF-8 output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

passed = 0
failed = 0
warnings = 0


def header(text):
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def check(req_id, description, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] [{req_id}] {description}")
    else:
        failed += 1
        print(f"  [FAIL] [{req_id}] {description}")
        if detail:
            print(f"         -> {detail}")


def warn(msg):
    global warnings
    warnings += 1
    print(f"  [WARN] {msg}")


def read_file(rel_path):
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def file_exists(rel_path):
    return os.path.exists(os.path.join(PROJECT_ROOT, rel_path))


# =========================================================
# Requirement 1: user-onboarding/SKILL.md
# =========================================================
def test_requirement_1():
    header("Requirement 1: User Onboarding Skill")

    check("1.1", "skills/user-onboarding/SKILL.md exists",
          file_exists("skills/user-onboarding/SKILL.md"),
          "File not found at skills/user-onboarding/SKILL.md")

    content = read_file("skills/user-onboarding/SKILL.md")
    if not content:
        check("1.2", "File contains markdown content", False, "Could not read file")
        return

    check("1.2", "File contains markdown content (>500 chars)",
          len(content) > 500,
          f"File is only {len(content)} chars, expected substantial content")

    has_domains = any(kw in content.lower() for kw in
                      ["domain", "programming language", "technical interest", "technical domains"])
    check("1.3", "Specifies questions for technical domains", has_domains,
          "Missing questions about technical domains/programming languages")

    has_level = any(kw in content.lower() for kw in
                    ["experience level", "experience", "junior", "mid-level", "senior"])
    check("1.4", "Specifies questions for experience level", has_level,
          "Missing questions about experience level")

    has_goals = any(kw in content.lower() for kw in
                    ["learning goal", "goals", "preparing for interview", "learning"])
    check("1.5", "Specifies questions for learning goals", has_goals,
          "Missing questions about learning goals")

    has_flow = any(kw in content.lower() for kw in
                   ["greet", "welcome", "step 1", "step 2", "flow", "onboarding flow"])
    check("1.6", "Defines a conversational onboarding flow", has_flow,
          "Missing conversational flow structure")


# =========================================================
# Requirement 2: daily-quiz/SKILL.md
# =========================================================
def test_requirement_2():
    header("Requirement 2: Daily Quiz Skill")

    check("2.1", "skills/daily-quiz/SKILL.md exists",
          file_exists("skills/daily-quiz/SKILL.md"),
          "File not found at skills/daily-quiz/SKILL.md")

    content = read_file("skills/daily-quiz/SKILL.md")
    if not content:
        check("2.2", "File contains markdown content", False, "Could not read file")
        return

    check("2.2", "File contains markdown content (>500 chars)",
          len(content) > 500,
          f"File is only {len(content)} chars")

    check("2.3", "Specifies use of web_search tool",
          "web_search" in content,
          "Missing reference to web_search tool")

    has_5_questions = any(kw in content for kw in
                         ["5 interview questions", "exactly 5", "5 questions",
                          "Generate exactly 5", "five interview questions"])
    check("2.4", "Instructs agent to generate 5 interview questions",
          has_5_questions, "Missing instruction for exactly 5 questions")

    has_tidbits = any(kw in content for kw in ["3-5", "3 to 5", "3--5", "tidbits"])
    check("2.5", "Instructs agent to generate 3-5 technical tidbits",
          has_tidbits, "Missing instruction for 3-5 tidbits")


# =========================================================
# Requirement 3: Persistent memory storage
# =========================================================
def test_requirement_3():
    header("Requirement 3: Persistent Memory Storage")

    content = read_file("skills/user-onboarding/SKILL.md")
    if not content:
        check("3.1", "Onboarding skill readable", False, "Could not read file")
        return

    check("3.1", "References memory_store tool",
          "memory_store" in content,
          "Missing reference to memory_store tool")

    check("3.2", 'Schema includes "domains" field',
          '"domains"' in content, 'Missing "domains" field in schema')

    check("3.3", 'Schema includes "level" field',
          '"level"' in content, 'Missing "level" field in schema')

    check("3.4", 'Schema includes "goals" field',
          '"goals"' in content, 'Missing "goals" field in schema')

    check("3.5", 'Schema includes "timezone" field',
          '"timezone"' in content, 'Missing "timezone" field in schema')

    check("3.6", "Uses user_profile_{{user.id}} as memory key",
          "user_profile_{{user.id}}" in content,
          "Missing user_profile_{{user.id}} key pattern")


# =========================================================
# Requirement 4: Cron job configuration
# =========================================================
def test_requirement_4():
    header("Requirement 4: Cron Job Configuration")

    config = read_file("config/openclaw.json") or ""
    readme = read_file("README.md") or ""
    all_content = config + readme

    check("4.1", 'Cron job named "nightly-tech-brief"',
          "nightly-tech-brief" in all_content,
          "Missing cron job name 'nightly-tech-brief'")

    check("4.2", 'Schedule set to "0 21 * * *" (9 PM daily)',
          "0 21 * * *" in all_content,
          "Missing cron schedule '0 21 * * *'")

    check("4.3", "Cron job uses timezone configuration",
          "timezone" in all_content.lower() or "--tz" in all_content,
          "Missing timezone configuration")

    check("4.4", "Cron job references daily-quiz skill",
          "daily-quiz" in all_content or "daily_quiz" in all_content,
          "Missing reference to daily-quiz skill")


# =========================================================
# Requirement 5: Auto-trigger onboarding
# =========================================================
def test_requirement_5():
    header("Requirement 5: Auto-Trigger Onboarding for New Users")

    config = read_file("config/openclaw.json") or ""
    readme = read_file("README.md") or ""
    all_content = config + readme

    has_standing = any(kw in all_content for kw in
                       ["standing-orders", "standingOrders", "Standing Order"])
    check("5.1", "Standing Order mechanism is implemented",
          has_standing, "Missing Standing Order implementation")

    has_doc = any(kw in readme for kw in
                  ["Standing Order", "standing-orders", "trigger-user-onboarding"])
    check("5.2", "Trigger method documented in README.md",
          has_doc, "Missing documentation of onboarding trigger")

    has_check = "user_profile_{{user.id}}" in all_content and "does not exist" in all_content
    check("5.3", 'Condition checks memory for new user detection',
          has_check, "Missing memory-based condition")


# =========================================================
# Requirement 6: Telegram message format
# =========================================================
def test_requirement_6():
    header("Requirement 6: Daily Message Format")

    content = read_file("skills/daily-quiz/SKILL.md")
    if not content:
        check("6.1", "Daily quiz skill readable", False, "Could not read file")
        return

    check("6.1", "Message sent via Telegram",
          "telegram" in content.lower(), "Missing Telegram reference")

    check("6.2", "Uses Markdown formatting",
          any(kw in content.lower() for kw in ["markdown", "bold"]),
          "Missing Markdown formatting spec")

    check("6.3", 'Contains "Your Daily Tech Brief" title',
          "Your Daily Tech Brief" in content, "Missing main title")

    check("6.4", 'Has "Interview Questions" section',
          "Interview Questions" in content, "Missing Interview Questions section")

    check("6.5", 'Has "Tidbits" section',
          "Tidbits" in content, "Missing Tidbits section")

    has_q1_to_q5 = all(f"Q{i}" in content for i in range(1, 6))
    check("6.6", "Template shows exactly 5 questions (Q1-Q5)",
          has_q1_to_q5, "Missing Q1-Q5 markers")

    check("6.7", 'Contains reply prompt for "answers" and "more"',
          "answers" in content.lower() and "more" in content.lower(),
          "Missing reply prompt")


# =========================================================
# Requirement 7: openclaw.json configuration
# =========================================================
def test_requirement_7():
    header("Requirement 7: Configuration File")

    check("7.1", "config/openclaw.json exists",
          file_exists("config/openclaw.json"),
          "File not found")

    content = read_file("config/openclaw.json")
    if not content:
        check("7.2", "Config readable", False, "Could not read file")
        return

    readme = read_file("README.md") or ""
    check("7.2", "Config referenced in README",
          "openclaw.json" in readme, "Missing in README")

    check("7.3", "Defines LLM model configuration",
          any(kw in content for kw in ["ollama", "openai", "llm", "model"]),
          "Missing model config")

    check("7.4", "Shows Telegram plugin setup",
          "telegram" in content.lower() and "plugin" in content.lower(),
          "Missing Telegram plugin")

    # Check for real secrets
    secret_patterns = [
        r'\d{9,10}:[A-Za-z0-9_-]{35}',
        r'sk-[A-Za-z0-9]{20,}',
        r'sk-ant-[A-Za-z0-9]{20,}',
    ]
    has_real_secrets = any(re.search(p, content) for p in secret_patterns)
    check("7.5", "CRITICAL: No real secrets in config",
          not has_real_secrets, "REAL SECRETS DETECTED!")

    check("7.6", "Uses placeholders/env vars for secrets",
          any(kw in content for kw in ["YOUR_TOKEN", "${env.", "YOUR_"]),
          "Missing placeholder references")


# =========================================================
# Requirement 8: README.md quality
# =========================================================
def test_requirement_8():
    header("Requirement 8: README.md Documentation")

    check("8.1", "README.md exists",
          file_exists("README.md"), "File not found")

    content = read_file("README.md")
    if not content:
        check("8.2", "README readable", False, "Could not read file")
        return

    check("8.2", "README is substantial (>2000 chars)",
          len(content) > 2000,
          f"Only {len(content)} chars")

    check("8.3", "Contains setup instructions",
          any(kw in content.lower() for kw in
              ["step 1", "setup", "installation", "quick start"]),
          "Missing setup instructions")

    check("8.4", "Contains running instructions",
          any(kw in content for kw in
              ["gateway start", "docker compose up", "openclaw"]),
          "Missing running instructions")

    check("8.5", "Documents onboarding trigger design decision",
          any(kw in content.lower() for kw in
              ["design decision", "design choice", "rationale", "standing order vs"]),
          "Missing design decision documentation")


# =========================================================
# Requirement 9: web_search usage
# =========================================================
def test_requirement_9():
    header("Requirement 9: Intelligent Web Search Usage")

    content = read_file("skills/daily-quiz/SKILL.md")
    if not content:
        check("9.1", "Daily quiz skill readable", False)
        return

    check("9.1", "Agent invokes web_search tool",
          "web_search" in content, "Missing web_search")

    check("9.2", "Search queries relevant to user's domains",
          any(kw in content.lower() for kw in
              ["domains", "user's specified", "preferences"]),
          "Missing domain-relevant search")

    check("9.3", "Instructs agent to look for fresh content",
          any(kw in content.lower() for kw in
              ["recent", "fresh", "latest", "freshness", "last 7 days"]),
          "Missing freshness instruction")

    check("9.4", "Provides example search queries",
          any(kw in content.lower() for kw in
              ["sample search", "example", "search query"]),
          "Missing example queries")


# =========================================================
# Requirement 10: Containerization
# =========================================================
def test_requirement_10():
    header("Requirement 10: Containerization")

    check("10.1", "Dockerfile exists",
          file_exists("Dockerfile"), "File not found")

    dockerfile = read_file("Dockerfile")
    if dockerfile:
        check("10.2", "Dockerfile has valid FROM instruction",
              "FROM" in dockerfile, "Missing FROM")

        check("10.3", "Dockerfile uses Node.js base image",
              "node" in dockerfile.lower(), "Missing Node.js image")

        check("10.4", "Dockerfile installs OpenClaw",
              "openclaw" in dockerfile.lower(), "Missing OpenClaw install")

    check("10.5", "docker-compose.yml exists",
          file_exists("docker-compose.yml"), "File not found")

    compose = read_file("docker-compose.yml")
    if compose:
        check("10.6", "docker-compose.yml defines services",
              "services" in compose, "Missing services section")

        check("10.7", "Includes OpenClaw gateway service",
              "openclaw" in compose.lower() and "gateway" in compose.lower(),
              "Missing gateway service")

        check("10.8", "Uses persistent volumes",
              "volumes" in compose, "Missing volumes")

    check("10.9", ".env.example exists",
          file_exists(".env.example"), "File not found")

    env = read_file(".env.example")
    if env:
        check("10.10", ".env.example has TELEGRAM_BOT_TOKEN",
              "TELEGRAM_BOT_TOKEN" in env, "Missing TELEGRAM_BOT_TOKEN")

        check("10.11", ".env.example has LLM config vars",
              any(kw in env for kw in ["LLM_PROVIDER", "LLM_MODEL", "OLLAMA"]),
              "Missing LLM config vars")


# =========================================================
# Bonus checks
# =========================================================
def test_bonus():
    header("Bonus: Additional Quality Checks")

    check("B.1", ".gitignore exists",
          file_exists(".gitignore"), "Missing .gitignore")

    gi = read_file(".gitignore")
    if gi:
        check("B.2", ".gitignore excludes .env files",
              ".env" in gi, "Secrets could be committed!")

    onb = read_file("skills/user-onboarding/SKILL.md")
    if onb:
        check("B.3", "Onboarding skill has YAML frontmatter",
              onb.strip().startswith("---"), "Missing frontmatter")

    quiz = read_file("skills/daily-quiz/SKILL.md")
    if quiz:
        check("B.4", "Daily quiz skill has YAML frontmatter",
              quiz.strip().startswith("---"), "Missing frontmatter")

    df = read_file("Dockerfile")
    if df:
        check("B.5", "Dockerfile uses multi-stage build",
              df.count("FROM ") >= 2, "Single-stage only")

    compose = read_file("docker-compose.yml")
    if compose:
        check("B.6", "docker-compose.yml includes Ollama service",
              "ollama" in compose.lower(), "Missing Ollama")

    readme = read_file("README.md")
    if readme:
        check("B.7", "README includes architecture section",
              "architecture" in readme.lower(), "Missing architecture")

        check("B.8", "README includes troubleshooting section",
              "troubleshoot" in readme.lower(), "Missing troubleshooting")


# =========================================================
# Main
# =========================================================
def main():
    print("")
    print("=" * 60)
    print("  AI Learning Assistant - Submission Validator v1.0")
    print("  Checking all 10 core requirements + bonus checks")
    print("=" * 60)
    print(f"  Project root: {PROJECT_ROOT}\n")

    test_requirement_1()
    test_requirement_2()
    test_requirement_3()
    test_requirement_4()
    test_requirement_5()
    test_requirement_6()
    test_requirement_7()
    test_requirement_8()
    test_requirement_9()
    test_requirement_10()
    test_bonus()

    total = passed + failed
    pct = (passed / total * 100) if total > 0 else 0

    print(f"\n{'=' * 60}")
    print(f"  RESULTS SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Passed:   {passed}/{total}")
    print(f"  Failed:   {failed}/{total}")
    print(f"  Warnings: {warnings}")
    print(f"  Score:    {pct:.1f}%")

    if failed == 0:
        print(f"\n  ALL CHECKS PASSED! Submission is ready.\n")
    else:
        print(f"\n  {failed} check(s) failed. Review above.\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

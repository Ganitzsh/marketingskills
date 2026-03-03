#!/usr/bin/env python3
"""
Regenerates .claude-plugin/marketplace.json and skills/*/.claude-plugin/plugin.json
from the SKILL.md files in skills/. Run after syncing with upstream.
"""
import os
import re
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")


def extract_frontmatter(content: str) -> dict:
    desc_match = re.search(
        r"^description:\s*(.+?)(?:\nmetadata:|\n[a-z]+:)", content, re.MULTILINE | re.DOTALL
    )
    description = (
        desc_match.group(1).strip().replace("\n", " ").replace("  ", " ").strip("\"'")
        if desc_match
        else ""
    )
    ver_match = re.search(r"version:\s*([^\n]+)", content)
    version = ver_match.group(1).strip() if ver_match else "1.0.0"
    return {"description": description[:200], "version": version}


def main() -> None:
    plugins = []

    for skill_name in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        skill_md = os.path.join(skill_path, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue

        with open(skill_md) as f:
            content = f.read()

        meta = extract_frontmatter(content)

        # Write plugin.json
        plugin_dir = os.path.join(skill_path, ".claude-plugin")
        os.makedirs(plugin_dir, exist_ok=True)
        plugin = {
            "name": skill_name,
            "description": meta["description"],
            "version": meta["version"],
            "skills": ["../SKILL.md"],
        }
        with open(os.path.join(plugin_dir, "plugin.json"), "w") as f:
            json.dump(plugin, f, indent=2)

        plugins.append(
            {
                "name": skill_name,
                "source": f"./skills/{skill_name}",
                "description": meta["description"],
            }
        )

    # Write marketplace.json
    marketplace = {
        "name": "marketing-skills",
        "owner": {
            "name": "Ganitzsh",
            "url": "https://github.com/Ganitzsh/marketingskills",
        },
        "description": (
            f"{len(plugins)} marketing skills for Claude — CRO, copywriting, SEO, "
            "content, analytics, growth engineering. Fork of coreyhaines31/marketingskills."
        ),
        "upstream": "https://github.com/coreyhaines31/marketingskills",
        "plugins": plugins,
    }

    out_dir = os.path.join(ROOT, ".claude-plugin")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "marketplace.json"), "w") as f:
        json.dump(marketplace, f, indent=2)

    print(f"Generated marketplace.json with {len(plugins)} plugins + {len(plugins)} plugin.json files")


if __name__ == "__main__":
    main()

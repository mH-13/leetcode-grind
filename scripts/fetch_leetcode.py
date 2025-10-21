#!/usr/bin/env python3
"""
Fetch LeetCode problem details from URL or problem slug.
Usage: python scripts/fetch_leetcode.py <url_or_slug>
"""
import sys
import re
import json
try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not found")
    print("Install it with: pip install requests")
    sys.exit(1)

def extract_slug(input_str):
    """Extract problem slug from URL or return as-is."""
    # Check if it's a URL
    url_match = re.search(r'leetcode\.com/problems/([^/]+)', input_str)
    if url_match:
        return url_match.group(1)
    # Otherwise assume it's already a slug
    return input_str.strip('/')

def fetch_problem_details(slug):
    """Fetch problem details from LeetCode GraphQL API."""
    url = "https://leetcode.com/graphql"

    query = """
    query getQuestionDetail($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        questionFrontendId
        title
        titleSlug
        difficulty
        topicTags {
          name
          slug
        }
        content
        codeSnippets {
          lang
          code
        }
      }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "query": query,
        "variables": {"titleSlug": slug}
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'data' not in data or not data['data']['question']:
            print(f"❌ Problem not found: {slug}")
            return None

        return data['data']['question']
    except Exception as e:
        print(f"❌ Error fetching problem: {e}")
        return None

def normalize_tag(tag):
    """Normalize tag names to match your system."""
    tag_map = {
        "Array": "array",
        "String": "string",
        "Hash Table": "hashmap",
        "Two Pointers": "two-pointers",
        "Sliding Window": "sliding-window",
        "Prefix Sum": "prefix-sum",
        "Binary Search": "binary-search",
        "Greedy": "greedy",
        "Depth-First Search": "dfs",
        "Breadth-First Search": "bfs",
        "Union Find": "union-find",
        "Heap (Priority Queue)": "heap",
        "Stack": "stack",
        "Queue": "queue",
        "Tree": "tree",
        "Binary Tree": "binary-tree",
        "Binary Search Tree": "bst",
        "Dynamic Programming": "dp",
        "Sorting": "sorting",
        "Simulation": "simulation",
        "Bit Manipulation": "bit",
        "Linked List": "linked-list",
        "Math": "math",
        "Design": "design",
        "Backtracking": "backtracking",
        "Trie": "trie",
        "Divide and Conquer": "divide-and-conquer",
        "Recursion": "recursion",
        "Memoization": "memo"
    }
    return tag_map.get(tag, tag.lower().replace(" ", "-"))

def display_problem(problem):
    """Display problem details in a formatted way."""
    tags = [normalize_tag(tag['name']) for tag in problem['topicTags']]
    tags_str = ", ".join(tags)

    print("\n" + "="*60)
    print(f"✅ Problem Found!")
    print("="*60)
    print(f"ID:         {problem['questionFrontendId']}")
    print(f"Title:      {problem['title']}")
    print(f"Slug:       {problem['titleSlug']}")
    print(f"Difficulty: {problem['difficulty']}")
    print(f"Tags:       {tags_str}")
    print(f"Link:       https://leetcode.com/problems/{problem['titleSlug']}/")
    print("="*60)

    # Find Python code snippet
    python_snippet = None
    for snippet in problem.get('codeSnippets', []):
        if snippet['lang'] in ['Python', 'Python3']:
            python_snippet = snippet['code']
            break

    if python_snippet:
        print("\n📝 Python Template:")
        print("-"*60)
        print(python_snippet)
        print("-"*60)

    print("\n💡 Quick Commands:")
    print(f"\n# Use with daily.py (answer prompts with these values):")
    print(f"ID:         {problem['questionFrontendId']}")
    print(f"Title:      {problem['title']}")
    print(f"Slug:       {problem['titleSlug']}")
    print(f"Difficulty: {problem['difficulty']}")
    print(f"Tags:       {tags_str}")

    print(f"\n# Or use with new.py:")
    cmd = f"python scripts/new.py --type py --track leetcode-75 \\\n"
    cmd += f"  --id {problem['questionFrontendId']} \\\n"
    cmd += f"  --slug {problem['titleSlug']} \\\n"
    cmd += f"  --title \"{problem['title']}\""
    print(cmd)

    return {
        'id': problem['questionFrontendId'],
        'title': problem['title'],
        'slug': problem['titleSlug'],
        'difficulty': problem['difficulty'],
        'tags': tags_str
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/fetch_leetcode.py <url_or_slug>")
        print("\nExamples:")
        print("  python scripts/fetch_leetcode.py https://leetcode.com/problems/two-sum/")
        print("  python scripts/fetch_leetcode.py two-sum")
        sys.exit(1)

    input_str = sys.argv[1]
    slug = extract_slug(input_str)

    print(f"🔍 Fetching problem: {slug}")
    problem = fetch_problem_details(slug)

    if problem:
        details = display_problem(problem)

        # Optionally save to a temp file for the wizard to read
        import os
        from pathlib import Path
        temp_file = Path.home() / '.leetcode_problem.json'
        with open(temp_file, 'w') as f:
            json.dump(details, f)
        print(f"\n💾 Details saved to: {temp_file}")
        print("   (daily.py can auto-read these values!)")

if __name__ == "__main__":
    main()

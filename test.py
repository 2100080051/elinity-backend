import os

def get_repo_structure(base_dir, max_depth=3):
    tree = []
    base_depth = base_dir.rstrip(os.sep).count(os.sep)
    for root, dirs, files in os.walk(base_dir):
        depth = root.count(os.sep) - base_depth
        if depth < max_depth:
            indent = "    " * depth
            tree.append(f"{indent}{os.path.basename(root)}/")
            for f in files:
                tree.append(f"{indent}    {f}")
    return "\n".join(tree)

print(get_repo_structure(".", max_depth=3))

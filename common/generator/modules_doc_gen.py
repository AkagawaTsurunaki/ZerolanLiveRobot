from common.generator.doc_gen import _get_sub_packages


def services_doc_gen():
    m_ls = _get_sub_packages("services")
    lines = []
    for m in m_ls:
        if "__markdown_doc__" in dir(m):
            lines.append(f"### {m.__name__}\n\n")
            lines.append(m.__markdown_doc__ + "\n\n")

    with open("services.md", "w+", encoding="utf-8") as f:
        f.writelines(lines)


services_doc_gen()
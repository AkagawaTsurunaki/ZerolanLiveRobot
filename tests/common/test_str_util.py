from common.utils.str_util import remove_md_blocks


def test_remove_md_blocks():
    """Comprehensive test suite"""

    # 1. Standard code block (with language identifier)
    input1 = "```python\nprint('hello')\n```"
    expected1 = "print('hello')"
    result1 = remove_md_blocks(input1)
    assert result1 == expected1, f"Test 1 failed: expected {repr(expected1)}, got {repr(result1)}"
    print("✓ Test 1 passed: Standard code block (with language identifier)")

    # 2. Standard code block (without language identifier)
    input2 = "```\nprint('hello')\n```"
    expected2 = "print('hello')"
    result2 = remove_md_blocks(input2)
    assert result2 == expected2, f"Test 2 failed: expected {repr(expected2)}, got {repr(result2)}"
    print("✓ Test 2 passed: Standard code block (without language identifier)")

    # 3. Multi-line code
    input3 = """```javascript
function add(a, b) {
    return a + b;
}
```"""
    expected3 = """function add(a, b) {
    return a + b;
}"""
    result3 = remove_md_blocks(input3)
    assert result3 == expected3, f"Test 3 failed: expected {repr(expected3)}, got {repr(result3)}"
    print("✓ Test 3 passed: Multi-line code")

    # 4. Code with blank lines
    input4 = "```\nline1\n\nline2\n```"
    expected4 = "line1\n\nline2"
    result4 = remove_md_blocks(input4)
    assert result4 == expected4, f"Test 4 failed: expected {repr(expected4)}, got {repr(result4)}"
    print("✓ Test 4 passed: Code with blank lines")

    # 5. No markdown code block markers (should not change)
    input5 = "print('no markdown')"
    expected5 = "print('no markdown')"
    result5 = remove_md_blocks(input5)
    assert result5 == expected5, f"Test 5 failed: expected {repr(expected5)}, got {repr(result5)}"
    print("✓ Test 5 passed: No markdown code block markers")

    # 6. Only opening ``` (incomplete code block)
    input6 = "```\nprint('test')"
    expected6 = "```\nprint('test')"  # return original content
    result6 = remove_md_blocks(input6)
    assert result6 == expected6, f"Test 6 failed: expected {repr(expected6)}, got {repr(result6)}"
    print("✓ Test 6 passed: Incomplete code block (no closing)")

    # 7. Only closing ``` (incomplete code block)
    input7 = "print('test')\n```"
    expected7 = "print('test')\n```"  # return original content
    result7 = remove_md_blocks(input7)
    assert result7 == expected7, f"Test 7 failed: expected {repr(expected7)}, got {repr(result7)}"
    print("✓ Test 7 passed: Incomplete code block (no opening)")

    # 8. Empty string
    input8 = ""
    expected8 = ""
    result8 = remove_md_blocks(input8)
    assert result8 == expected8, f"Test 8 failed: expected {repr(expected8)}, got {repr(result8)}"
    print("✓ Test 8 passed: Empty string")

    # 9. None input
    input9 = None
    expected9 = None
    result9 = remove_md_blocks(input9)
    assert result9 == expected9, f"Test 9 failed: expected {repr(expected9)}, got {repr(result9)}"
    print("✓ Test 9 passed: None input")

    # 10. Code block with only newlines
    input10 = "```\n\n```"
    expected10 = ""  # content is empty, should be empty string after stripping
    result10 = remove_md_blocks(input10)
    assert result10 == expected10, f"Test 10 failed: expected {repr(expected10)}, got {repr(result10)}"
    print("✓ Test 10 passed: Code block with only newlines")

    # 11. Language identifier followed by extra spaces (should still recognize)
    input11 = "```python   \nprint('test')\n```"
    expected11 = "print('test')"
    result11 = remove_md_blocks(input11)
    assert result11 == expected11, f"Test 11 failed: expected {repr(expected11)}, got {repr(result11)}"
    print("✓ Test 11 passed: Language identifier with trailing spaces")

    # 12. Code content with leading/trailing spaces (internal spaces preserved, external stripped)
    input12 = "```\n  indented_code  \n```"
    expected12 = "indented_code"  # .strip() removes leading/trailing spaces
    result12 = remove_md_blocks(input12)
    assert result12 == expected12, f"Test 12 failed: expected {repr(expected12)}, got {repr(result12)}"
    print("✓ Test 12 passed: Code content with indentation")

    # 13. Code block containing backticks (should handle correctly)
    input13 = "```\ncode with `backticks`\n```"
    expected13 = "code with `backticks`"
    result13 = remove_md_blocks(input13)
    assert result13 == expected13, f"Test 13 failed: expected {repr(expected13)}, got {repr(result13)}"
    print("✓ Test 13 passed: Code block containing backticks")

    # 14. Extra whitespace at beginning and end
    input14 = "   ```\ncode\n```   "
    expected14 = "code"
    result14 = remove_md_blocks(input14)
    assert result14 == expected14, f"Test 14 failed: expected {repr(expected14)}, got {repr(result14)}"
    print("✓ Test 14 passed: Extra whitespace at beginning and end")

    # 15. Complex language identifier (e.g., ```c++ or ```cpp)
    input15 = "```cpp\n#include <iostream>\n```"
    expected15 = "#include <iostream>"
    result15 = remove_md_blocks(input15)
    assert result15 == expected15, f"Test 15 failed: expected {repr(expected15)}, got {repr(result15)}"
    print("✓ Test 15 passed: Complex language identifier (cpp)")

    print("\n" + "=" * 50)
    print("All 15 test cases passed!")
    print("=" * 50)

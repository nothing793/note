/* MathJax 配置：配合 pymdownx.arithmatex（generic 模式）使用。
 * arithmatex 会把 $...$ / $$...$$ 转成 \(...\) / \[...\]，并且只给数学片段加
 * class="arithmatex"，所以这里只处理 .arithmatex，避免误伤正文里的 $ 与反斜杠。 */
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};

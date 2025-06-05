// convert.js
const fs = require('fs');
const path = require('path');
const markdownIt = require('markdown-it');
const markdownItAttrs = require('markdown-it-attrs');
const md = markdownIt().use(markdownItAttrs);

/**
 * 计算相对路径
 * @param {string} from - 起始目录
 * @param {string} to - 目标目录
 * @returns {string} 相对路径
 */
function getRelativePath(from, to) {
  const fromDir = path.dirname(from);
  const relativePath = path.relative(fromDir, to);
  return relativePath.replace(/\\/g, '/'); // 将反斜杠替换为斜杠
}

/**
 * 将 Markdown 文件转换为 HTML 文件
 * @param {string} filePath - Markdown 文件路径
 */
function convertMarkdownToHtml(filePath) {
  const markdownContent = fs.readFileSync(filePath, 'utf8').replace(/"""/g, '```');  
  const htmlContent = md.render(markdownContent);
  const title = path.basename(filePath, '.md').replace(/^\d+_/, '').replace(/_/g, ' ');

  // 获取对应的 Python 文件路径
  const pythonFilePath = filePath.replace(/\.md$/, '.py');
  let pythonContent = '';

  // 读取 Python 文件内容
  if (fs.existsSync(pythonFilePath)) {
    pythonContent = fs.readFileSync(pythonFilePath, 'utf8');
  } else {
    pythonContent = '对应的 Python 文件不存在。';
  }

  // 获取 CSS 和 JS 文件的相对路径
  const cssPath = getRelativePath(filePath, path.join(__dirname, 'markdown.css'));
  const jsPath = getRelativePath(filePath, path.join(__dirname, 'markdown.js'));

  const outputHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.4.0/styles/default.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.4.0/highlight.min.js"></script>
  <script>hljs.highlightAll();</script>
  <title>${title}</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=STIX+Two+Math&display=swap">
  <link rel="stylesheet" href="${cssPath}">
  <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <script src="${jsPath}"></script>
</head>
<body>
  <div class="container">
    ${htmlContent}
    <h3>Python 文件</h3>
    <pre><code>${pythonContent}</code></pre>
  </div>
</body>
</html>
  `;
  const outputFilePath = filePath.replace(/\.md$/, '.html');
  fs.writeFileSync(outputFilePath, outputHtml);
  console.log(`Converted: ${filePath} -> ${outputFilePath}`);
}

/**
 * 遍历目录并转换所有 Markdown 文件
 * @param {string} dir - 起始目录
 * @param {Array} links - 保存 HTML 文件链接的数组
 */
function traverseDirectory(dir, links) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat.isDirectory()) {
      traverseDirectory(filePath, links);
    } else if (filePath.endsWith('.md')) {
      convertMarkdownToHtml(filePath);
      links.push(filePath.replace(/\.md$/, '.html'));
    }
  });
}

/**
 * 生成 index.html 文件
 * @param {Array} links - HTML 文件链接数组
 */

function generateIndexHtml(links) {
  // 构建目录树
  const tree = {};
  links.forEach(link => {
    const parts = link.split('/');
    let current = tree;
    parts.forEach((part, index) => {
      // 去除前缀编号，并将下划线替换为空格
      const cleanPart = part.replace(/^\d+_/, '').replace(/_/g, ' ');
      if (!current[cleanPart]) {
        current[cleanPart] = (index === parts.length - 1) ? link : {};
      }
      current = current[cleanPart];
    });
  });

  // 生成HTML内容
  function renderTree(node, depth = 0) {
    const keys = Object.keys(node);
    return keys.map(key => {
      if (typeof node[key] === 'string') {
        return `<div class="link-item"><a href="${node[key]}">${key}</a></div>`;
      } else {
        const headingTag = `h${Math.min(depth + 1, 6)}`; // 标题标签，最多到 h6
        return `
          <${headingTag}>${key}</${headingTag}>
          <div class="tree-container">
            ${renderTree(node[key], depth + 1)}
          </div>
        `;
      }
    }).join('\n');
  }

  const indexContent = `
  <!DOCTYPE html>
  <html lang="zh">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index Page</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <div class="container">
      <h1>Index Page</h1>
      <div class="tree-container">
        ${renderTree(tree)}
      </div>
    </div>
  </body>
  </html>
  `;

  fs.writeFileSync('index.html', indexContent);
  console.log('Generated: index.html');
}

// 起始目录
const startDir = '.';
const links = [];
traverseDirectory(startDir, links);
generateIndexHtml(links);
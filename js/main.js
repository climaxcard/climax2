// 年号
const y = document.getElementById('year');
if (y) y.textContent = new Date().getFullYear();

// 現在ページを自動でactive表示（URL末尾で判定）
const path = location.pathname.split('/').pop() || 'index.html';
for (const a of document.querySelectorAll('nav a')) {
  const href = a.getAttribute('href');
  if ((path === 'index.html' && href.endsWith('index.html')) || href.endsWith(path)) {
    a.classList.add('active');
  }
}

// Keep the same section and a validated public campaign tag when switching.
// Static hrefs remain functional without JavaScript. Never copy auth queries.
(function () {
  var tag = new URLSearchParams(location.search).get('k') || '';
  document.querySelectorAll('[data-language-link]').forEach(function (link) {
    var target = new URL(link.getAttribute('href'), location.href);
    if (/^[a-z0-9-]{1,30}$/i.test(tag)) target.searchParams.set('k', tag);
    target.hash = location.hash;
    link.href = target.pathname + target.search + target.hash;
  });
  window.addEventListener('hashchange', function () {
    document.querySelectorAll('[data-language-link]').forEach(function (link) {
      var target = new URL(link.href);
      target.hash = location.hash;
      link.href = target.pathname + target.search + target.hash;
    });
  });
})();

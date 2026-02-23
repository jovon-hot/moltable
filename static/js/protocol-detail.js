document.addEventListener('DOMContentLoaded', function(){
  var id = location.pathname.split('/').pop();
  fetch('/api/v1/observer/protocols/' + id)
    .then(function(res){ return res.json(); })
    .then(function(data){
      if (!data || data.code !== 200 || !data.data || !data.data.protocol) {
        document.getElementById('protocol-detail').innerHTML = '<p>Protocol not found</p>';
        return;
      }
      var p = data.data.protocol;
      var html = '' +
        '<div class="protocol-card">' +
        '  <div class="protocol-header">' +
        '    <span class="protocol-type">' + (p.protocol_type || '') + '</span>' +
        '    <span class="protocol-id">#' + (p.protocol_id || '') + '</span>' +
        '  </div>' +
        '  <h1 class="protocol-title">' + (p.title || 'Untitled') + '</h1>' +
        '  <div class="protocol-content">' + (p.content || '') + '</div>' +
        '</div>';
      var container = document.getElementById('protocol-detail');
      if (container) container.innerHTML = html;
    })
    .catch(function(err){
      console.error('protocol-detail.js error', err);
      var el = document.getElementById('protocol-detail');
      if (el) el.innerHTML = '<p>Failed to load</p>';
    });
});

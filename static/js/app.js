function toggleSidebar() {
    var target = document.getElementById('sidebar');
    target.classList.toggle('hide') ;
    target = document.getElementById('contents');
    target.classList.toggle('sidebar-hidden')
  };
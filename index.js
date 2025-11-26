const logoutBtn = document.getElementById('logoutBtn');

function logoutBtnInnerHtml() {
  const currentUser = sessionStorage.getItem('currentUser');
  
  if(currentUser) {
    logoutBtn.innerHTML = 'تسجيل الخروج';
  } else {
    logoutBtn.innerHTML = '<a href="sample_login.html">تسجيل الدخول</a>';
  }
}


logoutBtn.addEventListener('click', function(e) {
  const currentUser = sessionStorage.getItem('currentUser');
  
  if(currentUser) {
    
    e.preventDefault();
    sessionStorage.removeItem('currentUser');
    logoutBtnInnerHtml(); 
    console.log('User logged out successfully');
  }
  
});

window.addEventListener('DOMContentLoaded', function() {
  logoutBtnInnerHtml();
});
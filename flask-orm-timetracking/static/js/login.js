$(document).ready(function () {
  // Custom SweetAlert2 theme for dark theme
  const darkSwal = Swal.mixin({
    background: '#1e1e1e',
    color: '#e0e0e0',
    customClass: {
      popup: 'dark-card',
      confirmButton: 'dark-btn dark-btn-primary',
      cancelButton: 'dark-btn dark-btn-danger'
    },
    buttonsStyling: false
  });

  $("#loginForm").on("submit", function (e) {
    e.preventDefault();
    
    const username = $("#username").val();
    const password = $("#password").val();
    
    if (!username || !password) {
      darkSwal.fire({
        title: 'Attention',
        text: 'Veuillez remplir tous les champs',
        icon: 'warning'
      });
      return;
    }
    
    // Show loading state
    const submitBtn = $(this).find('button[type="submit"]');
    const originalText = submitBtn.html();
    submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Connexion...');
    submitBtn.prop('disabled', true);
    
    $.ajax({
      url: "/login",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ username, password }),
      success: function (res) {
        // Store token in both localStorage and as a cookie for redundancy
        localStorage.setItem("access_token", res.access_token);
        
        // Check if we're logged in successfully
        if (res.logged_in) {
          darkSwal.fire({
            title: 'Succès',
            text: 'Connexion réussie!',
            icon: 'success',
            showConfirmButton: false,
            timer: 1500
          }).then(() => {
            window.location.href = "/";
          });
        }
      },
      error: function (err) {
        // Reset button state
        submitBtn.html(originalText);
        submitBtn.prop('disabled', false);
        
        darkSwal.fire({
          title: 'Erreur',
          text: err.responseJSON?.msg || 'Échec de la connexion',
          icon: 'error'
        });
      }
    });
  });
});

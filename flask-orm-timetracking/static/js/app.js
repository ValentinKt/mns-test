$(document).ready(function () {
  // Configure jQuery AJAX to always send credentials
  $.ajaxSetup({
    xhrFields: {
      withCredentials: true
    }
  });
  
  // Function to check if user is logged in - update to check multiple cookies
  function isLoggedIn() {
    // Check for any of our session cookies
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if ((name === 'user_session' && value === 'active') || 
          (name === 'session_persistent' && value === 'true')) {
        return true;
      }
    }
    return false;
  }
  
  // Make the token refresh more aggressive
  function setupTokenRefresh() {
    // Refresh every 30 minutes (1800000 ms) instead of 45
    const refreshInterval = 30 * 60 * 1000;
    
    setInterval(() => {
      if (isLoggedIn()) {
        refreshToken()
          .then(() => console.log("Scheduled token refresh completed"))
          .catch(err => {
            console.error("Scheduled token refresh failed", err);
            // Don't redirect to login here, just log the error
          });
      }
    }, refreshInterval);
    
    // Also refresh immediately when the page loads
    if (isLoggedIn()) {
      refreshToken()
        .then(() => console.log("Initial token refresh completed"))
        .catch(err => console.error("Initial token refresh failed", err));
    }
  }
  
  // Function to refresh the access token
  // Function to refresh the access token
  function refreshToken() {
    console.log("Attempting to refresh token...");
    return new Promise((resolve, reject) => {
      $.ajax({
        url: "/api/refresh",
        method: "POST",
        xhrFields: {
          withCredentials: true  // Important: ensures cookies are sent with request
        },
        success: function(response) {
          console.log("Token refreshed successfully", response);
          resolve(true);
        },
        error: function(err) {
          console.error("Token refresh failed", err);
          // If refresh fails, redirect to login
          window.location.href = "/login";
          reject(err);
        }
      });
    });
  }
  
  // Set up periodic token refresh (every 45 minutes)
  function setupTokenRefresh() {
    // Refresh every 45 minutes (2700000 ms)
    const refreshInterval = 45 * 60 * 1000;
    
    setInterval(() => {
      if (isLoggedIn()) {
        refreshToken()
          .then(() => console.log("Scheduled token refresh completed"))
          .catch(err => console.error("Scheduled token refresh failed", err));
      }
    }, refreshInterval);
    
    // Also refresh immediately when the page loads
    if (isLoggedIn()) {
      refreshToken()
        .then(() => console.log("Initial token refresh completed"))
        .catch(err => console.error("Initial token refresh failed", err));
    }
  }
  
  // Initialize token refresh mechanism
  setupTokenRefresh();
  
  // Function to make authenticated API requests with token refresh capability
  function apiRequest(url, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
      const options = {
        url: url,
        method: method,
        headers: { 
          'Content-Type': 'application/json'
        },
        xhrFields: {
          withCredentials: true  // Important: ensures cookies are sent with request
        },
        success: function(response) {
          resolve(response);
        },
        error: function(err) {
          // If we get a 401 Unauthorized error, try to refresh the token
          if (err.status === 401) {
            refreshToken()
              .then(() => {
                // Retry the original request after token refresh
                return apiRequest(url, method, data);
              })
              .then(resolve)
              .catch(reject);
          } else {
            reject(err);
          }
        }
      };
      
      if (data && (method === 'POST' || method === 'PUT')) {
        options.data = JSON.stringify(data);
      }
      
      $.ajax(options);
    });
  }
  
  // Function to handle logout
  function logout() {
    return apiRequest('/api/logout', 'POST')  // Use the /api/logout endpoint consistently
      .then(() => {
        window.location.href = "/login";
      })
      .catch(err => {
        console.error("Logout failed:", err);
        // Redirect to login anyway
        window.location.href = "/login";
      });
  }
  
  // Update the logout button handler
  $("#logout").on("click", function () {
    darkSwal.fire({
      title: 'Déconnexion',
      text: 'Êtes-vous sûr de vouloir vous déconnecter ?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Oui, déconnexion',
      cancelButtonText: 'Annuler'
    }).then((result) => {
      if (result.isConfirmed) {
        // Call the logout function that uses the correct endpoint
        logout();
      }
    });
  });
  
  // Check if user is logged in
  if (!isLoggedIn()) {
    window.location.href = "/login";
    return;
  }
  
  // Add logout button event handler
  $("#logoutBtn").on("click", function(e) {
    e.preventDefault();
    logout();
  });
  
  // Function to get the JWT token from various sources
  function getJwtToken() {
    // First try localStorage
    const token = localStorage.getItem("access_token");
    if (token) {
      return token;
    }
    
    // Then try cookies (if httpOnly is false)
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'access_token_cookie') {
        return value;
      }
    }
    
    return null;
  }
  
  // Custom SweetAlert2 theme for dark theme
  const darkSwal = Swal.mixin({
    background: '#1e1e1e',
    color: '#e0e0e0',
    customClass: {
      popup: 'dark-card',
      confirmButton: 'dark-btn dark-btn-primary ms-2',
      cancelButton: 'dark-btn dark-btn-danger me-2'
    },
    buttonsStyling: false
  });
  
  // Check if we have a token
  const token = getJwtToken();
  if (!token) {
    window.location.href = "/login";
    return;
  }
  
  // Initialize the app
  fetchSessions();
  fetchActivities();
  
  // Logout handler
  $("#logout").on("click", function () {
    darkSwal.fire({
      title: 'Déconnexion',
      text: 'Êtes-vous sûr de vouloir vous déconnecter ?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Oui, déconnexion',
      cancelButtonText: 'Annuler'
    }).then((result) => {
      if (result.isConfirmed) {
        // Clear localStorage token
        localStorage.removeItem("access_token");
        
        // Call logout endpoint to clear the cookie
        apiRequest('/logout', 'POST')
          .then(() => {
            window.location.href = "/login";
          })
          .catch(() => {
            // Even if the request fails, redirect to login
            window.location.href = "/login";
          });
      }
    });
  });
  
  // Get user info
  apiRequest('/api/me')
    .then(res => {
      $("#username").text(res.username).addClass('animate__animated animate__fadeIn');
    })
    .catch(err => console.error('Failed to get user info:', err));
  
  // Form submission handler for sessions
  $("#sessionForm").on("submit", function (e) {
    e.preventDefault();
    const activity = $("#activity").val();
    const duration = $("#duration").val();
    
    if (!activity) {
      darkSwal.fire({
        title: 'Attention',
        text: 'Veuillez sélectionner une activité',
        icon: 'warning'
      });
      return;
    }
    
    if (!duration || duration <= 0) {
      darkSwal.fire({
        title: 'Attention',
        text: 'Veuillez entrer une durée valide',
        icon: 'warning'
      });
      return;
    }
    
    // Show loading state
    const submitBtn = $(this).find('button[type="submit"]');
    const originalText = submitBtn.html();
    submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Enregistrement...');
    submitBtn.prop('disabled', true);
    
    apiRequest('/api/sessions', 'POST', {
      activity,
      duration,
      date: new Date().toISOString()
    })
    .then(res => {
      darkSwal.fire({
        title: 'Succès',
        text: res.message,
        icon: 'success'
      });
      fetchSessions();
      $("#sessionForm")[0].reset();
      
      // Reset button state
      submitBtn.html(originalText);
      submitBtn.prop('disabled', false);
    })
    .catch(err => {
      console.error('Failed to add session:', err);
      
      // Reset button state
      submitBtn.html(originalText);
      submitBtn.prop('disabled', false);
      
      darkSwal.fire({
        title: 'Erreur',
        text: 'Échec de l\'ajout de la session',
        icon: 'error'
      });
    });
  });
  
  // Form submission handler for activities
  $("#activityForm").on("submit", function (e) {
    e.preventDefault();
    const name = $("#newActivity").val().trim();
    
    if (!name) {
      darkSwal.fire({
        title: 'Attention',
        text: 'Veuillez entrer un nom d\'activité',
        icon: 'warning'
      });
      return;
    }
    
    // Show loading state
    const submitBtn = $(this).find('button[type="submit"]');
    const originalText = submitBtn.html();
    submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Ajout...');
    submitBtn.prop('disabled', true);
    
    apiRequest('/api/activities', 'POST', { name })
      .then(res => {
        darkSwal.fire({
          title: 'Succès',
          text: res.message,
          icon: 'success'
        });
        fetchActivities();
        $("#activityForm")[0].reset();
        
        // Reset button state
        submitBtn.html(originalText);
        submitBtn.prop('disabled', false);
      })
      .catch(err => {
        // Reset button state
        submitBtn.html(originalText);
        submitBtn.prop('disabled', false);
        
        if (err.responseJSON && err.responseJSON.message) {
          darkSwal.fire({
            title: 'Erreur',
            text: err.responseJSON.message,
            icon: 'error'
          });
        } else {
          console.error('Failed to add activity:', err);
          darkSwal.fire({
            title: 'Erreur',
            text: 'Échec de l\'ajout de l\'activité',
            icon: 'error'
          });
        }
      });
  });
  
  // Event delegation for delete activity buttons
  $("#activityList").on("click", ".delete-activity", function() {
    const activity = $(this).data("activity");
    
    darkSwal.fire({
      title: 'Confirmation',
      text: `Êtes-vous sûr de vouloir supprimer l'activité "${activity}" ?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Oui, supprimer',
      cancelButtonText: 'Annuler'
    }).then((result) => {
      if (result.isConfirmed) {
        // Show loading state
        $(this).html('<i class="fas fa-spinner fa-spin"></i>');
        $(this).prop('disabled', true);
        
        apiRequest(`/api/activities/${encodeURIComponent(activity)}`, 'DELETE')
          .then(res => {
            darkSwal.fire({
              title: 'Supprimé!',
              text: res.message || "Activité supprimée avec succès",
              icon: 'success'
            });
            fetchActivities();
            fetchSessions(); // Refresh sessions as some might use this activity
          })
          .catch(err => {
            if (err.responseJSON && err.responseJSON.message) {
              darkSwal.fire({
                title: 'Erreur',
                text: err.responseJSON.message,
                icon: 'error'
              });
            } else {
              console.error('Failed to delete activity:', err);
              darkSwal.fire({
                title: 'Erreur',
                text: "Erreur lors de la suppression de l'activité",
                icon: 'error'
              });
            }
          });
      }
    });
  });
  
  // Function to fetch sessions
  function fetchSessions() {
    apiRequest('/api/sessions')
      .then(data => {
        $("#sessionList").empty();
        if (data.length === 0) {
          $("#sessionList").append(`
            <div class="dark-card text-center text-muted">
              <i class="fas fa-info-circle fa-2x mb-3"></i>
              <p>Aucune session enregistrée</p>
            </div>
          `);
          return;
        }
        
        data.forEach((session, index) => {
          const date = new Date(session.date).toLocaleString();
          const animationDelay = index * 100; // Stagger the animations
          
          $("#sessionList").append(`
            <div class="dark-list-item fade-in" style="animation-delay: ${animationDelay}ms">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <i class="fas fa-tasks text-primary me-2"></i>
                  <strong>${session.activity}</strong> 
                  <span class="text-muted">- ${session.duration} min</span>
                </div>
                <div class="dark-badge">
                  <i class="far fa-calendar-alt me-1"></i>${date}
                </div>
              </div>
            </div>
          `);
        });
      })
      .catch(err => console.error('Failed to fetch sessions:', err));
  }
  
  // Function to fetch activities
  function fetchActivities() {
    apiRequest('/api/activities')
      .then(data => {
        // Update the activity list
        $("#activityList").empty();
        if (data.length === 0) {
          $("#activityList").append(`
            <div class="dark-card text-center text-muted">
              <i class="fas fa-info-circle fa-2x mb-3"></i>
              <p>Aucune activité disponible</p>
            </div>
          `);
        } else {
          data.forEach((activity, index) => {
            const animationDelay = index * 100; // Stagger the animations
            
            $("#activityList").append(`
              <div class="dark-list-item d-flex justify-content-between align-items-center fade-in" style="animation-delay: ${animationDelay}ms">
                <span><i class="fas fa-tag text-success me-2"></i>${activity}</span>
                <button class="dark-btn dark-btn-danger delete-activity" data-activity="${activity}">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            `);
          });
        }
        
        // Update the activity dropdown
        const activitySelect = $("#activity");
        activitySelect.find('option:not(:first)').remove();
        
        data.forEach(activity => {
          activitySelect.append(`<option value="${activity}">${activity}</option>`);
        });
      })
      .catch(err => console.error('Failed to fetch activities:', err));
  }
});

document.addEventListener("DOMContentLoaded", function () {

  function setupToggle(passwordId, toggleId) {
    const passwordField = document.getElementById(passwordId);
    const toggleIcon = document.getElementById(toggleId);

    if (!passwordField || !toggleIcon) {
      return;
    }

    passwordField.type = "password";
    toggleIcon.className = "fa fa-eye-slash password-toggle";

    toggleIcon.onclick = function (e) {
      if (e) e.preventDefault();

      if (passwordField.type === "password") {
        passwordField.type = "text";
        this.className = "fa fa-eye password-toggle";
        console.log("Changed to: fa-eye, new class:", this.className);
      } else {
        passwordField.type = "password";
        this.className = "fa fa-eye-slash password-toggle";
      }

      return false;
    };
  }

  setTimeout(function () {
    setupToggle("password", "password_toggle_public");

    setupToggle("password", "password_toggle_signup");
    setupToggle("confirm_password", "password_toggle_confirm");
    setupToggle("password", "password_toggle_reset");
    setupToggle("confirm_password", "password_toggle_reset_confirm");

  }, 300);
});

if (typeof jQuery !== "undefined") {
  jQuery(document).ready(function () {

    jQuery("#password_toggle_public").on("click", function (e) {
      e.preventDefault();
      var pwField = jQuery("#password");
      if (pwField.attr("type") === "password") {
        pwField.attr("type", "text");
        jQuery(this).attr("class", "fa fa-eye password-toggle");
      } else {
        pwField.attr("type", "password");
        jQuery(this).attr("class", "fa fa-eye-slash password-toggle");
      }
      return false;
    });

    jQuery("#password_toggle_signup, #password_toggle_reset").on(
      "click",
      function (e) {
        e.preventDefault();
        var pwField = jQuery("#password");
        if (pwField.attr("type") === "password") {
          pwField.attr("type", "text");
          jQuery(this).attr("class", "fa fa-eye password-toggle");
        } else {
          pwField.attr("type", "password");
          jQuery(this).attr("class", "fa fa-eye-slash password-toggle");
        }
        return false;
      }
    );

    jQuery("#password_toggle_confirm, #password_toggle_reset_confirm").on(
      "click",
      function (e) {
        e.preventDefault();
        var pwField = jQuery("#confirm_password");
        if (pwField.attr("type") === "password") {
          pwField.attr("type", "text");
          jQuery(this).attr("class", "fa fa-eye password-toggle");
        } else {
          pwField.attr("type", "password");
          jQuery(this).attr("class", "fa fa-eye-slash password-toggle");
        }
        return false;
      }
    );
  });
}

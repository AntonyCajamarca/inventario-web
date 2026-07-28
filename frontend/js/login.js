/* ============================================================
   login.js — Logica de la pagina de inicio de sesion
   ============================================================ */

document.getElementById("year").textContent = new Date().getFullYear();

// Si ya hay una sesion activa, ir directo al panel
if (Auth.isLoggedIn()) {
  window.location.href = "/pages/dashboard.html";
}

document.getElementById("togglePassword").addEventListener("click", () => {
  const input = document.getElementById("password");
  const icon = document.querySelector("#togglePassword i");
  const isHidden = input.type === "password";
  input.type = isHidden ? "text" : "password";
  icon.className = isHidden ? "bi bi-eye-slash" : "bi bi-eye";
});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearAlert("alertBox");

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  const btn = document.getElementById("loginBtn");
  const btnText = document.getElementById("loginBtnText");
  const spinner = document.getElementById("loginBtnSpinner");

  btn.disabled = true;
  btnText.textContent = "Ingresando...";
  spinner.classList.remove("d-none");

  try {
    const data = await apiRequest("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      redirectOn401: false,
    });

    if (data) {
      Auth.setToken(data.access_token);
      Auth.setUser(data.user);
      window.location.href = "/pages/dashboard.html";
    }
  } catch (error) {
    showAlert("alertBox", `<i class="bi bi-exclamation-triangle-fill me-1"></i>${error.message}`);

    // Limpia la contraseña y deja el campo listo para reintentar
    const passwordInput = document.getElementById("password");
    passwordInput.value = "";
    passwordInput.focus();

    btn.disabled = false;
    btnText.textContent = "Ingresar";
    spinner.classList.add("d-none");
  }
});

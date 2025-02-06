//@see https://memberful.com/help/custom-development-and-api/sign-in-for-apps-via-oauth/

const DEBUG = true;

const baseUrl = DEBUG ? "http://localhost:8080" : "https://jupitersignal.memberful.com";

const authorizationUrl = new URL(`${baseUrl}/authorize`);
const tokenUrl = new URL(`${baseUrl}/token`);
const clientId = "Ov23liut9HTgjRSbkgCr"; // CHANGE ME
const redirectUrl = new URL("?callback=", currentUrl());

function currentUrl() {
  return new URL(window.location.href);
}

function isLoggedIn() {
  const accessToken = localStorage.getItem("memberful_access_token");
  const refreshToken = localStorage.getItem("memberful_refresh_token");
  const expiresAt = localStorage.getItem("memberful_access_token_expires_at");

  return accessToken && refreshToken && expiresAt && new Date(expiresAt) > new Date();
}

function isTokenExpired() {
  const expiresAt = localStorage.getItem("memberful_access_token_expires_at");
  return new Date(expiresAt) < new Date();
}

function generateRandomString(byteLength) {
  const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
  let randomString = "";
  for (let i = 0; i < byteLength; i++) {
    randomString += charset.charAt(Math.floor(Math.random() * charset.length));
  }

  return randomString;
}

function sha256(plain) {
  const encoder = new TextEncoder();
  const data = encoder.encode(plain);
  return window.crypto.subtle.digest("SHA-256", data);
}

function base64urlencode(a) {
  var str = "";
  var bytes = new Uint8Array(a);
  var len = bytes.byteLength;
  for (var i = 0; i < len; i++) {
    str += String.fromCharCode(bytes[i]);
  }
  return btoa(str)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

async function memberfulLogin() {
  const codeVerifier = generateRandomString(128);
  const codeVerifierHash = await sha256(codeVerifier);
  const codeChallenge = base64urlencode(codeVerifierHash);
  const state = generateRandomString(16);

  authorizationUrl.searchParams.append("response_type", "code");
  authorizationUrl.searchParams.append("state", state);
  authorizationUrl.searchParams.append("client_id", clientId);
  authorizationUrl.searchParams.append("redirect_uri", redirectUrl.toString());
  authorizationUrl.searchParams.append("code_challenge", codeChallenge);
  authorizationUrl.searchParams.append("code_challenge_method", "S256");

  // Before redirecting, save the code verifier and state in local storage
  localStorage.setItem("memberful_oauth_code_verifier", codeVerifier);
  localStorage.setItem("memberful_oauth_state", state);

  // Redirect the user to the authorization URL
  window.location.href = authorizationUrl.toString();
}

// Expose the function to the global scope
window.memberfulLogin = memberfulLogin;


// Callback handling
async function callbackHandler() {
  const code = currentUrl().searchParams.get("code");
  const state = currentUrl().searchParams.get("state");

  // Verify the state to prevent CSRF attacks
  if (state !== localStorage.getItem("memberful_oauth_state")) {
    alert("Invalid state parameter");
    exitCallback();
    return;
  }

  // Exchange the code for an access token
  const tokenRequest = new Request(tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      grant_type: "authorization_code",
      code: code,
      code_verifier: localStorage.getItem("memberful_oauth_code_verifier"),
    })
  });

  // Send the request
  const response = await fetch(tokenRequest);
  const tokenResponse = await response.json();

  // Save the access token and refresh token in local storage
  localStorage.setItem("memberful_access_token", tokenResponse.access_token);
  localStorage.setItem("memberful_refresh_token", tokenResponse.refresh_token);
  const expiresAt = new Date(Date.now() + tokenResponse.expires_in * 1000);
  localStorage.setItem("memberful_access_token_expires_at", expiresAt.toISOString());

  // Clean up local storage
  localStorage.removeItem("memberful_oauth_code_verifier");
  localStorage.removeItem("memberful_oauth_state");

  // Clean up the URL
  exitCallback();
}

function exitCallback() {
  const url = currentUrl();
  url.search = "";
  console.log("Redirecting to", url.toString());
  window.location.href = url.toString();
}

// Fire the callback handler if the URL contains a callback query parameter
if (currentUrl().searchParams.has("callback")) callbackHandler();

// Api request
async function fetchUserData() {
  const accessToken = localStorage.getItem("memberful_access_token");
  const apiUrl = new URL(`${baseUrl}/api/graphql/member`);
  apiUrl.searchParams.append("query",
    "{currentMember {fullName email subscriptions {product {name}}}}"
  );

  if (DEBUG) {
    return {
      fullName: "John Doe",
      email: "john.doe@example.org",
      subscriptions: [
        { product: { name: "Product 1" } },
        { product: { name: "Product 2" } },
      ],
    };
  }

  const response = await fetch(apiUrl, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const data = await response.json();
  return data.data.currentMember;
};

async function handleTokenRefresh() {
  const tokenRequest = new Request(tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      grant_type: "refresh_tokenssss",
      refresh_token: localStorage.getItem("memberful_refresh_token"),
    })
  });

  // Send the request
  let response;
  try {
    response = await fetch(tokenRequest);
  } catch (error) {
    console.error("Failed to refresh token", error);
    // Clear the local storage and reload the page to restart the flow
    localStorage.removeItem("memberful_access_token");
    localStorage.removeItem("memberful_refresh_token");
    localStorage.removeItem("memberful_access_token_expires_at");

    return window.location.reload();
  }
  const tokenResponse = await response.json();

  // Save the new access token and refresh token in local storage
  localStorage.setItem("memberful_access_token", tokenResponse.access_token);
  localStorage.setItem("memberful_refresh_token", tokenResponse.refresh_token);
  const expiresAt = new Date(Date.now() + tokenResponse.expires_in * 1000);
  localStorage.setItem("memberful_access_token_expires_at", expiresAt.toISOString());

  // Reload the page to restart te flow
  return window.location.reload();
}

function populateDOMWithUserData(userData) {
  // Hide buttton, unhide form
  document.getElementById("memberfulLoginButton").classList.add("is-hidden");
  document.getElementById("memberfulForm").classList.remove("is-hidden");

  // Replace sender
  document.querySelector("#memberfulForm input[name='from']").value = `${userData.fullName} <${userData.email}>`;
}

// Maniupulate DOM based on login status (after page is done loading)
document.addEventListener("DOMContentLoaded", async function () {
  // Handle case where the access token has expired and we need to refresh it
  if (isTokenExpired()) {
    return handleTokenRefresh();
  }

  console.log("Logged in?", isLoggedIn());
  if (isLoggedIn()) {
    // Fetch user data
    const userData = await fetchUserData();
    console.log("User data", userData);
    populateDOMWithUserData(userData);
  }
});
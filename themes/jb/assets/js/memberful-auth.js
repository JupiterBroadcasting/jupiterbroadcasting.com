//@see https://memberful.com/help/custom-development-and-api/sign-in-for-apps-via-oauth/

function currentUrl() {
  return new URL(window.location.href)
}

function generateRandomString(byteLength) {
  const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
  let randomString = ""
  for (let i = 0; i < byteLength; i++) {
    randomString += charset.charAt(Math.floor(Math.random() * charset.length))
  }

  return randomString
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

const authorizationUrl = new URL("http://localhost:8080/authorize")
const tokenUrl = new URL("http://localhost:8080/token")
const clientId = "Ov23liut9HTgjRSbkgCr" // CHANGE ME
const redirectUrl = new URL("?callback=", currentUrl())

async function memberlyLogin() {
  const codeVerifier = generateRandomString(128)
  const codeVerifierHash = await sha256(codeVerifier)
  const codeChallenge = base64urlencode(codeVerifierHash)
  const state = generateRandomString(16)

  authorizationUrl.searchParams.append("response_type", "code")
  authorizationUrl.searchParams.append("state", state)
  authorizationUrl.searchParams.append("client_id", clientId)
  authorizationUrl.searchParams.append("redirect_uri", redirectUrl.toString())
  authorizationUrl.searchParams.append("code_challenge", codeChallenge)
  authorizationUrl.searchParams.append("code_challenge_method", "S256")

  // Before redirecting, save the code verifier and state in local storage
  localStorage.setItem("memberful_oauth_code_verifier", codeVerifier)
  localStorage.setItem("memberful_oauth_state", state)

  // Redirect the user to the authorization URL
  window.location.href = authorizationUrl.toString()
}

// Expose the function to the global scope
window.memberlyLogin = memberlyLogin

// Callback handling
async function callbackHandler() {
  if (!currentUrl().searchParams.has("code") || !currentUrl().searchParams.has("state") || 
      localStorage.getItem("memberful_oauth_code_verifier") === null || 
      localStorage.getItem("memberful_oauth_state") === null) {
    return
  }

  const code = currentUrl().searchParams.get("code")
  const state = currentUrl().searchParams.get("state")

  // Verify the state to prevent CSRF attacks
  if (state !== localStorage.getItem("memberful_oauth_state")) {
    alert("Invalid state parameter")
    return
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
  })

  // Send the request
  const response = await fetch(tokenRequest)
  const tokenResponse = await response.json()

  // Save the access token and refresh token in local storage
  localStorage.setItem("memberful_access_token", tokenResponse.access_token)
  localStorage.setItem("memberful_refresh_token", tokenResponse.refresh_token)
  const expiresAt = new Date(Date.now() + tokenResponse.expires_in * 1000)
  localStorage.setItem("memberful_access_token_expires_at", expiresAt.toISOString())

  // Clean up local storage
  localStorage.removeItem("memberful_oauth_code_verifier")
  localStorage.removeItem("memberful_oauth_state")
}

// Fire the callback handler if the URL contains a callback query parameter
if (currentUrl().searchParams.has("callback")) callbackHandler()

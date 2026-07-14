const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;

let currentMax = 100;
let currentProgress = 0;
let allVersions = [];
let allUsers = [];
let defaultDir = "";

// ── Random name detection (matches Python: r"(?i)^[a-z]+as[a-z]+\d{2}$") ──
function isRandomName(name) {
    return /^[a-z]+as[a-z]+\d{2}$/i.test(name);
}

// ── Load everything in parallel for instant startup ──
async function fetchInitialData() {
    try {
        // Fire all three requests at the same time — no waiting in sequence
        const [dir, versions, users] = await Promise.all([
            invoke("get_default_directory"),
            invoke("get_versions").catch(() => []),   // network, may be slow — don't block
            invoke("get_users", { dir: localStorage.getItem("game-dir") || "" }),
        ]);

        defaultDir = dir;
        allVersions = versions;

        // If get_users was called with empty dir, reload with correct dir
        if (!localStorage.getItem("game-dir")) {
            allUsers = await invoke("get_users", { dir: defaultDir });
        } else {
            allUsers = users;
        }

        populateUserDropdown();
        updateVersionList();

        if (allUsers.length === 0) {
            generateAndSetRandomUser();
        } else {
            const userSelect = document.getElementById("username");
            const lastUser = localStorage.getItem("current_username");
            const found = allUsers.find(u => u.username === lastUser);
            if (found) {
                userSelect.value = lastUser;
                loadUserToUI(found);
            } else if (allUsers.length > 0) {
                userSelect.value = allUsers[0].username;
                loadUserToUI(allUsers[0]);
            }
        }
    } catch (e) {
        console.error("Error al cargar datos iniciales:", e);
    }
}

function populateUserDropdown() {
    const comboDropdown = document.getElementById("combo-dropdown");
    comboDropdown.innerHTML = "";
    allUsers.forEach(u => {
        let li = document.createElement("li");
        li.dataset.value = u.username;
        li.textContent = u.username;
        comboDropdown.appendChild(li);
    });
}

function loadUserToUI(user) {
    localStorage.setItem("java-path", user.java_executable || "");
    localStorage.setItem("jvm-args", user.jvm_args || "-Xmx2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC");
    localStorage.setItem("game-dir", user.advanced_options_directory || defaultDir);
    localStorage.setItem("chk-close-launcher", user.advanced_options_close_launcher ? "true" : "false");
    localStorage.setItem("chk-hide-log", user.hide_log ? "true" : "false");
    localStorage.setItem("chk-enable-uuid", user.enable_uuid ? "true" : "false");
    
    document.getElementById("custom-uuid").value = user.uuid || "";
    
    document.getElementById("label-uuid").style.display = user.enable_uuid ? "inline-block" : "none";
    document.getElementById("custom-uuid").style.display = user.enable_uuid ? "inline-block" : "none";
    
    let vType = user.type_version || "release";
    document.getElementById("chk-snapshot").checked = vType === "snapshot";
    document.getElementById("chk-beta").checked = vType === "beta";
    document.getElementById("chk-alpha").checked = vType === "alpha";
    document.getElementById("chk-especial").checked = vType === "especial";
    
    updateVersionList();
    
    if (user.selected_version) {
        setVersionValue(user.selected_version);
    }
    
    toggleLogAndUUID();
    updateUsernameColor(user.username);
    localStorage.setItem("current_username", user.username);
}

async function generateAndSetRandomUser() {
    try {
        const randomName = await invoke("generate_random_user");
        const userSelect = document.getElementById("username");
        // Just set the text — do NOT add to dropdown (like Python's entry_username.set())
        userSelect.value = randomName;
        
        localStorage.setItem("java-path", "");
        localStorage.setItem("jvm-args", "-Xmx2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC");
        localStorage.setItem("game-dir", defaultDir);
        localStorage.setItem("chk-close-launcher", "false");
        localStorage.setItem("chk-hide-log", "false");
        localStorage.setItem("chk-enable-uuid", "false");
        
        let generatedUuid = await invoke("generate_uuid_for_username", { username: randomName });
        document.getElementById("custom-uuid").value = generatedUuid;
        
        document.getElementById("label-uuid").style.display = "none";
        document.getElementById("custom-uuid").style.display = "none";
        
        document.getElementById("chk-snapshot").checked = false;
        document.getElementById("chk-beta").checked = false;
        document.getElementById("chk-alpha").checked = false;
        document.getElementById("chk-especial").checked = false;
        
        updateVersionList();
        toggleLogAndUUID();
        updateUsernameColor(randomName);
        localStorage.setItem("current_username", randomName);
    } catch (e) {
         console.error("Error generando usuario:", e);
    }
}

// Helper to set version combobox value
function setVersionValue(val) {
    const versionInput = document.getElementById("version");
    const dropdown = document.getElementById("version-dropdown");
    const items = dropdown.querySelectorAll("li");
    for (let i = 0; i < items.length; i++) {
        if (items[i].dataset.value === val) {
            versionInput.value = val;
            return true;
        }
    }
    return false;
}

function updateVersionList() {
    const showSnapshots = document.getElementById("chk-snapshot").checked;
    const showBeta = document.getElementById("chk-beta").checked;
    const showAlpha = document.getElementById("chk-alpha").checked;
    const showEspecial = document.getElementById("chk-especial").checked;
    
    const versionInput = document.getElementById("version");
    const versionDropdown = document.getElementById("version-dropdown");
    const previousSelection = versionInput.value;
    versionDropdown.innerHTML = "";
    
    const filtered = allVersions.filter(v => {
        let isSpecial = v.id.includes("forge") || v.id.includes("fabric") || v.id.includes("quilt");
        
        if (showEspecial) {
            return isSpecial;
        }
        
        let matchesType = false;
        if (showSnapshots && v.type === "snapshot") matchesType = true;
        if (showBeta && v.type === "old_beta") matchesType = true;
        if (showAlpha && v.type === "old_alpha") matchesType = true;
        
        if (showSnapshots || showBeta || showAlpha) {
            return matchesType;
        }
        
        return v.type === "release" && !isSpecial;
    });
    
    filtered.forEach(v => {
        let li = document.createElement("li");
        li.dataset.value = v.id;
        li.textContent = v.id;
        versionDropdown.appendChild(li);
    });
    
    if (previousSelection && !setVersionValue(previousSelection)) {
        const firstItem = versionDropdown.querySelector("li");
        versionInput.value = firstItem ? firstItem.dataset.value : "";
    } else if (!previousSelection) {
        const firstItem = versionDropdown.querySelector("li");
        versionInput.value = firstItem ? firstItem.dataset.value : "";
    }
}

async function saveCurrentSettings() {
    const username = document.getElementById("username").value;
    // Never save random-generated names (Python regex: ^[a-z]+as[a-z]+\d{2}$)
    if (!username || isRandomName(username)) return;
    
    let vType = "release";
    if (document.getElementById("chk-snapshot").checked) vType = "snapshot";
    if (document.getElementById("chk-beta").checked) vType = "beta";
    if (document.getElementById("chk-alpha").checked) vType = "alpha";
    if (document.getElementById("chk-especial").checked) vType = "especial";
    
    const userConfig = {
        username: username,
        uuid: document.getElementById("custom-uuid").value,
        selected_version: document.getElementById("version").value || "",
        type_version: vType,
        advanced_options_directory: localStorage.getItem("game-dir") || defaultDir,
        advanced_options_close_launcher: localStorage.getItem("chk-close-launcher") === "true",
        hide_log: localStorage.getItem("chk-hide-log") === "true",
        enable_uuid: localStorage.getItem("chk-enable-uuid") === "true",
        jvm_args: localStorage.getItem("jvm-args") || "",
        java_executable: localStorage.getItem("java-path") || "",
    };
    
    try {
        await invoke("save_user", { dir: userConfig.advanced_options_directory, user: userConfig });
    } catch (e) {
        console.error("Error saving user:", e);
    }
}

function logMessage(msg) {
    const logText = document.getElementById("log-text");
    logText.value += "[" + new Date().toLocaleTimeString() + "] " + msg + "\n";
    logText.scrollTop = logText.scrollHeight;
}

function toggleLogAndUUID() {
    const enableLog = localStorage.getItem("chk-hide-log") === "true";
    const enableUUID = localStorage.getItem("chk-enable-uuid") === "true";
    
    let w = enableLog ? 830 : 305;
    let h = enableUUID ? 192 : 160;
    
    invoke("resize_window", { width: w, height: h });
    
    if (enableLog) {
        document.getElementById("log-frame").style.display = "block";
        document.getElementById("log-frame").style.height = enableUUID ? "182px" : "150px";
    } else {
        document.getElementById("log-frame").style.display = "none";
    }
    
    if (enableUUID) {
        document.getElementById("btn-launch").style.top = "127px";
        document.getElementById("btn-close-game").style.top = "127px";
        document.getElementById("btn-toggle-advanced").style.top = "161px";
        document.getElementById("label-uuid").style.display = "inline-block";
        document.getElementById("custom-uuid").style.display = "inline-block";
    } else {
        document.getElementById("btn-launch").style.top = "96px";
        document.getElementById("btn-close-game").style.top = "96px";
        document.getElementById("btn-toggle-advanced").style.top = "130px";
        document.getElementById("label-uuid").style.display = "none";
        document.getElementById("custom-uuid").style.display = "none";
    }
}

function updateUsernameColor(username) {
    const el = document.getElementById("username");
    const uuidEl = document.getElementById("custom-uuid");
    
    if (username.length <= 2 || username.length > 15) {
        el.style.color = "red";
        uuidEl.style.color = "red";
    } else if (username.toLowerCase() === "random" || username.includes("as")) {
        el.style.color = "gray";
        uuidEl.style.color = "gray";
    } else {
        el.style.color = "black";
        uuidEl.style.color = "black";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchInitialData();
    
    document.getElementById("btn-random").addEventListener("click", generateAndSetRandomUser);
    
    // ── Username Combobox logic ──
    const comboBtn = document.getElementById("combo-btn");
    const comboDropdown = document.getElementById("combo-dropdown");
    const userSelect = document.getElementById("username");
    const versionSelect = document.getElementById("version");
    const btnLaunch = document.getElementById("btn-launch");
    const btnClose = document.getElementById("btn-close-game");

    // ── Version Combobox logic ──
    const versionComboBtn = document.getElementById("version-combo-btn");
    const versionDropdown = document.getElementById("version-dropdown");

    // ── Toggle helper ──
    function toggleDropdown(dropdown) {
        const wasOpen = dropdown.style.display === "block";
        closeAllDropdowns();
        if (!wasOpen) {
            dropdown.style.display = "block";
        }
    }

    function closeAllDropdowns() {
        comboDropdown.style.display = "none";
        versionDropdown.style.display = "none";
    }

    comboBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleDropdown(comboDropdown);
    });

    comboDropdown.addEventListener("click", (e) => {
        if (e.target.tagName === "LI") {
            userSelect.value = e.target.dataset.value;
            userSelect.dispatchEvent(new Event("change"));
            comboDropdown.style.display = "none";
        }
    });

    versionComboBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleDropdown(versionDropdown);
    });

    versionSelect.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleDropdown(versionDropdown);
    });

    versionDropdown.addEventListener("click", (e) => {
        if (e.target.tagName === "LI") {
            versionSelect.value = e.target.dataset.value;
            versionDropdown.style.display = "none";
        }
    });

    document.addEventListener("click", () => {
        closeAllDropdowns();
    });
    
    document.getElementById("username").addEventListener("change", async (e) => {
        const username = e.target.value;
        localStorage.setItem("current_username", username);
        const selected = allUsers.find(u => u.username === username);
        if (selected) {
            loadUserToUI(selected);
        } else {
            updateUsernameColor(username);
            let generatedUuid = await invoke("generate_uuid_for_username", { username: username });
            document.getElementById("custom-uuid").value = generatedUuid;
        }
    });
    
    document.getElementById("btn-toggle-advanced").addEventListener("click", async () => {
        await invoke("open_advanced_options");
    });
    
    // Checkbox radio behavior
    const checkboxes = ["chk-snapshot", "chk-beta", "chk-alpha", "chk-especial"];
    checkboxes.forEach(id => {
        document.getElementById(id).addEventListener("change", (e) => {
            if (e.target.checked) {
                checkboxes.forEach(otherId => {
                    if (otherId !== id) document.getElementById(otherId).checked = false;
                });
            }
            updateVersionList();
        });
    });
    
    listen("advanced-settings-applied", async (event) => {
        toggleLogAndUUID();
    });
    
    listen("save-and-close", async () => {
        await saveCurrentSettings();
        await invoke("force_close");
    });
    
    listen("install-status", (event) => {
        logMessage(event.payload);
    });

    listen("game-log", (event) => {
        logMessage(event.payload);
    });
    
    listen("install-max", (event) => {
        currentMax = event.payload;
        currentProgress = 0;
    });
    
    listen("install-progress", (event) => {
        currentProgress = event.payload;
        if (currentMax > 0 && currentProgress > 0 && currentProgress % Math.floor(currentMax/10) === 0) {
            logMessage("Progreso: " + currentProgress + "/" + currentMax);
        }
    });

    listen("game-exited", () => {
        logMessage("Minecraft se ha cerrado.");
        btnLaunch.disabled = false;
        btnClose.disabled = true;
        userSelect.disabled = false;
    });
    
    btnLaunch.addEventListener("click", async () => {
        const selectedVersion = versionSelect.value;
        const selectedUser = userSelect.value;
        
        if (!selectedVersion) return alert("Por favor, selecciona una versión.");
        
        let javaExec = localStorage.getItem("java-path");
        if (!javaExec) {
            javaExec = await invoke("resolve_java_path", { 
                version: selectedVersion, 
                gameDir: localStorage.getItem("game-dir") || defaultDir 
            });
        }
        
        btnLaunch.disabled = true;
        btnClose.disabled = false;
        userSelect.disabled = true;
        
        logMessage("Iniciando/Verificando instalación de " + selectedVersion + "...");
        
        const launchOptions = {
            username: selectedUser,
            uuid: localStorage.getItem("chk-enable-uuid") === "true" ? document.getElementById("custom-uuid").value : "",
            version: selectedVersion,
            jvm_args: localStorage.getItem("jvm-args") || "",
            java_executable: javaExec,
            close_launcher: localStorage.getItem("chk-close-launcher") === "true",
            game_directory: localStorage.getItem("game-dir") || defaultDir,
        };
        
        try {
            await invoke("launch_minecraft", { options: launchOptions });
            logMessage("Minecraft iniciado exitosamente.");
            
            if (launchOptions.close_launcher) {
                await saveCurrentSettings();
                await invoke("force_close");
            }
        } catch (e) {
            console.error("Error al lanzar:", e);
            logMessage("Error al lanzar: " + e);
            alert("Error al lanzar Minecraft:\n" + e);
            btnLaunch.disabled = false;
            btnClose.disabled = true;
            userSelect.disabled = false;
        }
    });

    btnClose.addEventListener("click", async () => {
        await invoke("kill_minecraft");
    });
});

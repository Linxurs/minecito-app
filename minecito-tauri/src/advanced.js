const { invoke } = window.__TAURI__.core;
const { emit } = window.__TAURI__.event;

document.addEventListener("DOMContentLoaded", () => {
    // Load from localStorage (shared with main.js)
    document.getElementById("jvm-args").value = localStorage.getItem("jvm-args") || "-Xmx2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC";
    document.getElementById("java-path").value = localStorage.getItem("java-path") || "";
    document.getElementById("game-dir").value = localStorage.getItem("game-dir") || "";
    document.getElementById("chk-close-launcher").checked = localStorage.getItem("chk-close-launcher") === "true";
    document.getElementById("chk-hide-log").checked = localStorage.getItem("chk-hide-log") === "true";
    document.getElementById("chk-enable-uuid").checked = localStorage.getItem("chk-enable-uuid") === "true";
    document.getElementById("chk-delete-user").checked = false;
    
    document.getElementById("btn-select-java").addEventListener("click", async () => {
        const p = await invoke("select_java_file");
        if (p) {
            document.getElementById("java-path").value = p;
        }
    });

    document.getElementById("btn-select-dir").addEventListener("click", async () => {
        const p = await invoke("select_minecraft_directory");
        if (p) {
            document.getElementById("game-dir").value = p;
        }
    });
    
    document.getElementById("btn-save-settings").addEventListener("click", async () => {
        if (document.getElementById("chk-delete-user").checked) {
            const username = localStorage.getItem("current_username");
            const gameDir = document.getElementById("game-dir").value;
            if (username && await invoke("ask_confirm", { title: "Eliminar Usuario", message: "¿Estás seguro de que quieres eliminar el usuario " + username + "?" })) {
                try {
                    await invoke("delete_user", { dir: gameDir, username: username });
                } catch(e) {}
            }
        } else {
            localStorage.setItem("jvm-args", document.getElementById("jvm-args").value);
            localStorage.setItem("java-path", document.getElementById("java-path").value);
            localStorage.setItem("game-dir", document.getElementById("game-dir").value);
            localStorage.setItem("chk-close-launcher", document.getElementById("chk-close-launcher").checked ? "true" : "false");
            localStorage.setItem("chk-hide-log", document.getElementById("chk-hide-log").checked ? "true" : "false");
            localStorage.setItem("chk-enable-uuid", document.getElementById("chk-enable-uuid").checked ? "true" : "false");
        }
        
        emit("advanced-settings-applied", {});
        invoke("close_advanced_options");
    });
    
    document.getElementById("btn-close-modal").addEventListener("click", () => {
        invoke("close_advanced_options");
    });
});


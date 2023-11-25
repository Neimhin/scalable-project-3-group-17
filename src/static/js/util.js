function load_cache_of_device(device_interface) {
    window.alert("nyi")
}

// contributors: NROBINSO
function endpoint(endpoint_name) {

    async function window_alert(r){
        window.alert(await r.text())
    }
    fetch(endpoint_name)
        .then(window_alert,console.error)
}

// # contributors: NROBINSO
function disconnect_a_random_device() {
    fetch("/disconnect_device")
        .then(async function(ok) {
            console.log(ok)
            new_adjacency_matrix()
        })
}
function load_cache_of_device(device_interface) {
    window.alert("nyi")
}

function endpoint(endpoint_name) {
    fetch(endpoint_name)
}

function disconnect_a_random_device() {
    fetch("/disconnect_device")
        .then(async function(ok) {
            console.log(ok)
            new_adjacency_matrix()
        })
}
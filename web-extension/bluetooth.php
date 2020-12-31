<?php
require_once "assets/php/main.php";
$headerTimingValue = 0;
function headerTiming($action, $addV="x-timing") {
	global $headerTimingValue;
	if ($action == "start") {
		$headerTimingValue = microtime(true);
	}
	if ($action == "set") {
		header("$addV: " . (microtime(true) - $headerTimingValue));
	}
}
function jarvisBluetoothExecute($arg) {
	$user = getJarvisConfig()["user"];
	$output = `sudo -u $user -- jarvis-bluetooth --$arg 2>&1`;
	$outputs = explode("{", $output, 2);
	$error = $outputs[0];
	$jsonOutput = json_decode("{" . $outputs[1], true);
	$jsonOutput["error"] .= $error;
	return $jsonOutput;
}
function jarvisBluetooth() {
	$result = [
		"errors" => [],
		"result" => []
	];

	$res = [];
	$available = [];
	$paired = [];
	$connected = [];

	headerTiming("start");
	if (isset($_GET["fast"])) {
		$res = jarvisBluetoothExecute("paired --connected");
		$paired = $res["result"][0];
		$connected = $res["result"][1];
		$result["result"] = $paired;
	} else {
		$res = jarvisBluetoothExecute("available --paired --connected");
		$available = $res["result"][0];
		$paired = $res["result"][1];
		$connected = $res["result"][2];
		$result["result"] = $available;
	}
	headerTiming("set", "x-timing-bluetooth-executable");

	for ($i=0; $i < count($paired); $i++) { 
		for ($j=0; $j < count($result["result"]); $j++) { 
			if ($paired[$i]["mac_address"] == $result["result"][$j]["mac_address"]) {
				$result["result"][$j]["paired"] = true;
			}
		}
	}

	$at_least_one_connected = false;
	// now check all the connected devices
	for ($i=0; $i < count($connected); $i++) { 
		for ($j=0; $j < count($result["result"]); $j++) { 
			if ($connected[$i]["mac_address"] == $result["result"][$j]["mac_address"]) {
				$result["result"][$j]["connected"] = true;
				$at_least_one_connected = true;
			}
		}
	}

	headerTiming("start");
	$cnf = getJarvisConfig();
	$loaded_apps = isset($cnf["loaded_apps"]) ? $cnf["loaded_apps"] : [];
	for ($i = 0; $i < count($loaded_apps); $i++) { 
		if ($loaded_apps[$i]["name"] == "headset") {
			$loaded_apps[$i]["web-extension"]["config"]["material_icon"] = $at_least_one_connected ? "bluetooth_connected" : "bluetooth";
		}
	}
	setJarvisConfig("loaded_apps", $loaded_apps);
	headerTiming("set", "x-timing-config-file");

	return $result;
}
if (isset($_GET["get-devices"])) {
	header("content-type: text/plain");
	$res = jarvisBluetooth();
	echo json_encode($res);
	die();
}
if (isset($_GET["pair"])) {
	if ($_GET["un"] == "true") {
		echo json_encode(jarvisBluetoothExecute("remove " . $_GET["mac"]));
	} else {
		echo json_encode(jarvisBluetoothExecute("pair " . $_GET["mac"]));
	}
	die();
}
if (isset($_GET["connect"])) {
	if ($_GET["un"] == "true") {
		echo json_encode(jarvisBluetoothExecute("disconnect " . $_GET["mac"]));
	} else {
		jarvisBluetoothExecute("trust " . $_GET["mac"]);
		echo json_encode(jarvisBluetoothExecute("connect " . $_GET["mac"]));
	}
	die();
}

$title = "Jarvis Bluetooth";
require "extension.php";
?>

<h1> <i>bluetooth</i> Bluetooth</h1>

<application>
	<table>
		<thead>
			<tr>
				<td>Name</td>
				<td>MAC</td>
				<td>Paired</td>
				<td>Connected</td>
				<td></td>
				<td></td>
			</tr>
		</thead>
		<tbody>
		</tbody>
	</table>
</application>


<script>
/* rewriting the get function to apply loading animation */
const get_old = get;
get = function(url, args) {
	document.querySelector("application").classList.add("loading");
	return new Promise(function(res, rej) {
		get_old(url, args).then((a,b,c,d,e,f) => {
			document.querySelector("application").classList.remove("loading");
			res(a,b,c,d,e,f);
		}).catch((e,f,g) => {
			document.querySelector("application").classList.remove("loading");
			rej(e,f,g);
		})
	});
}

/* bluetooth functions */
function bluetoothGetDevices(fast=false) {
	get(`?get-devices${fast ? "&fast" : ""}`).then(d => {
		d = JSON.parse(d);

		// generate the table code
		let code = "";
		let at_least_one_connected = false;
		if (d.errors.length == 0) {	
			d.result
				.sort((a,b) => Object.keys(b).length - Object.keys(a).length)
				.forEach(element => {
					if (element.connected) { at_least_one_connected = true; }
					code += `<tr>
								<td>${element.name.replace("<unknown>", "Unknown")}</td>
								<td>${element.mac_address}</td>
								<td>${element.paired ? "<span class='green'>Yes</span>" : "<span class='red'>No</span>"}</td>
								<td>${element.connected ? "<span class='green'>Yes</span>" : "<span class='red'>No</span>"}</td>
								<td><button onclick="bluetoothPair('${element.mac_address}', ${element.paired ? "true" : "false"})" class="iconbutton">${element.paired ? "Unpair" : "Pair"}</button></td>
								<td><button onclick="bluetoothConnect('${element.mac_address}', ${element.connected ? "true" : "false"})" class="iconbutton">${element.connected ? "Disconnect" : "Connect"}</button></td>
							</tr>`;
			});
		} else {
			code = `<tr><td colspan="6">An error occured: ${d.errors.join("<br>")}</td></tr>`;
		}
		document.querySelector("tbody").innerHTML = code;

		// modify the bluetooth symbol if a device is connected
		[...document.querySelectorAll("i")]
			.filter(i => i.innerHTML.includes("bluetooth"))
			.forEach(i => { i.innerHTML = at_least_one_connected ? "bluetooth_connected" : "bluetooth" });
		
		// automatically requery to get more results
		if (fast) { bluetoothGetDevices(); }
	}).catch(e => {
		document.querySelector("tbody").innerHTML = `<tr><td colspan="6">An unknown error occured:<br>${e}</td></tr>`;
	});
}
function bluetoothPair(mac, is_already_paired) {
	get(`?pair&un=${is_already_paired ? "true" : "false"}&mac=${mac}`).then(d => {
		d = JSON.parse(d);
		if (d.success) {
			launchAlert(console.info, "Success!", `Successfully ${is_already_paired ? "removed" : "paired"} this device!<br>${d.error}`);
			bluetoothGetDevices();
		} else {
			launchAlert(console.info, "Failed!", `Failed to ${is_already_paired ? "remove" : "pair"} this device!<br>${d.error}`);
		}
	})
}
function bluetoothConnect(mac, is_already_paired) {
	get(`?connect&un=${is_already_paired ? "true" : "false"}&mac=${mac}`).then(d => {
		d = JSON.parse(d);
		if (d.success) {
			launchAlert(console.info, "Success!", `Successfully ${is_already_paired ? "disconnected from" : "connected to"} this device!<br>${d.error}`);
			bluetoothGetDevices();
		} else {
			launchAlert(console.info, "Failed!", `Failed to ${is_already_paired ? "disconnect from" : "connect to"} this device!<br>${d.error}`);
		}
	})
}
bluetoothGetDevices(true);
setInterval(bluetoothGetDevices, 20 * 1000);
</script>
<style>
	table tr > td:nth-child(1) {	width: 200px !important;	}
	table tr > td:nth-child(2) {	width: 200px !important;	}
	table tr > td:nth-child(3) {	width: 75px !important;		}
	table tr > td:nth-child(4) {	width: 75px !important;		}
</style>
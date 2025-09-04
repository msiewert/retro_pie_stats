from datetime import datetime

from awscrt import mqtt
from awsiot import mqtt_connection_builder
import sys
import threading
import time
import argparse
import json

parser = argparse.ArgumentParser(description="Process RetroPie arguments.")
parser.add_argument("--action", type=str, help="The action being taken.")
parser.add_argument("--emulator", type=str, help="The emulator being used.")
parser.add_argument("--game", type=str, help="The name of the game.")
parser.add_argument("--endpoint", type=str, help="The IotCore endpoint.")
parser.add_argument("--ca_file", type=str, help="Path to ca_file.")
parser.add_argument("--cert", type=str, help="Path to cert file.")
parser.add_argument("--key", type=str, help="Path to key file.")

args = parser.parse_args()

print(f"emulator: {args.emulator}")
print(f"game: {args.game}")
print(f"action: {args.action}")
print(f"endpoint: {args.endpoint}")
print(f"ca_file: {args.ca_file}")
print(f"cert: {args.cert}")
print(f"key: {args.key}")

received_all_event = threading.Event()

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, dup, qos, retain, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    received_all_event.set()

# Callback when the connection successfully connects
def on_connection_success(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print("Connection Successful with return code: {} session present: {}".format(callback_data.return_code, callback_data.session_present))

# Callback when a connection attempt fails
def on_connection_failure(connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error))

# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(connection, callback_data):
    print("Connection closed")

if __name__ == '__main__':

    # Create a MQTT connection from the command line data
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=args.endpoint,
        port=8883,
        cert_filepath=args.cert,
        pri_key_filepath=args.key,
        ca_filepath=args.ca_file,
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id="retropie",
        clean_session=False,
        keep_alive_secs=30,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed)

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    message_count = 1
    message_topic = "game/stats"

    # given that args.game contains a string like /home/pi/RetroPie/roms/nes/Contra (USA).nes
    # we want to extract the game name, which is the last part of the string after the slash and before the .
    game = args.game.split("/")[-1].split(".")[0]

    print("Game Name: {}".format(game))

    #create an object to send to the server
    message = {
        "timestamp": datetime.now().isoformat(),
        "action": args.action,
        "emulator": args.emulator,
        "game": game,
    }

    # Subscribe
    print("Subscribing to topic '{}'...".format(message_topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=message_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    if message:
        if message_count == 0:
            print("Sending messages until program killed")
        else:
            print("Sending {} message(s)".format(message_count))

        publish_count = 1
        while (publish_count <= message_count) or (message_count == 0):
            print("Publishing message to topic '{}': {}".format(message_topic, message))
            message_json = json.dumps(message)
            mqtt_connection.publish(
                topic=message_topic,
                payload=message_json,
                qos=mqtt.QoS.AT_LEAST_ONCE)
            time.sleep(1)
            publish_count += 1

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if message_count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("message received.")

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")

import argparse
import json
from datetime import datetime

from awscrt import mqtt
from awsiot import mqtt_connection_builder

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


# Callback when connection is accidentally lost.
def on_connection_interrupted(_connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(_connection, return_code, session_present, **kwargs):
    print(
        "Connection resumed. return_code: {} session_present: {}".format(
            return_code, session_present
        )
    )


# Callback when the connection successfully connects
def on_connection_success(_connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionSuccessData)
    print(
        "Connection Successful with return code: {} session present: {}".format(
            callback_data.return_code, callback_data.session_present
        )
    )


# Callback when a connection attempt fails
def on_connection_failure(_connection, callback_data):
    assert isinstance(callback_data, mqtt.OnConnectionFailureData)
    print("Connection failed with error code: {}".format(callback_data.error))


# Callback when a connection has been disconnected or shutdown successfully
def on_connection_closed(_connection, callback_data):
    print("Connection closed")


if __name__ == "__main__":

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
        clean_session=True,
        keep_alive_secs=30,
        on_connection_success=on_connection_success,
        on_connection_failure=on_connection_failure,
        on_connection_closed=on_connection_closed,
    )

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    message_topic = "game/stats"

    # given that args.game contains a string like /home/pi/RetroPie/roms/nes/Contra (USA).nes
    # we want to extract the game name, which is the last part of the string after the slash and before the .
    game = args.game.split("/")[-1].split(".")[0]

    print("Game Name: {}".format(game))

    # create an object to send to the server
    message = {
        "timestamp": datetime.now().isoformat(),
        "action": args.action,
        "emulator": args.emulator,
        "game": game,
    }

    # Publish message
    print("Publishing message to topic '{}': {}".format(message_topic, message))
    message_json = json.dumps(message)
    publish_future = mqtt_connection.publish(
        topic=message_topic, payload=message_json, qos=mqtt.QoS.AT_LEAST_ONCE
    )

    # Wait for publish to complete
    publish_future.result()
    print("Message published successfully")

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")

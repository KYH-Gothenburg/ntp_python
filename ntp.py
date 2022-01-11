import datetime
import socket
import struct


def create_query_packet():
    # The query packet must always be 48 bytes long
    # We will only use the first byte, the other 47 bytes will
    # be left with zeros
    packet = bytearray(48)

    # First byte consists of 3 fields
    # First 2 bits: 11, leap second status unknown
    # Next 3 bits: 100, NTP version indicator, 100 = 4 = NTP version 4
    # Last 3 bits: 011, NTP mode indicator, 011 = 3 = client
    packet[0] = 0b11100011
    # packet[0] = 227
    return packet


def decode_message(msg):
    """
    Decode the NTP response message
    :param msg: bytearray, response from NTP server
    :return: datetime
    """
    # Extract the Transmit Timestamp from the message
    encoded = msg[40:48]

    # Unpack the encoded data into secnds and fractions of a second
    # ! means the data is stored in big-endian
    # I mean that there are two unsigned integers
    # First integer will end up in seconds, the second in fractions
    seconds, fractions = struct.unpack("!II", encoded)

    # NTP specs states that the time given is in seconds since 1 jan 1900
    base_time = datetime.datetime(1900, 1, 1)

    # Calculate how many days, hours, min and seconds since 1900-01-01
    offset = datetime.timedelta(seconds=seconds + fractions / 2**32)
    return base_time + offset


def main():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    query_packet = create_query_packet()
    udp_socket.sendto(query_packet, ("pool.ntp.org", 123))
    msg, address = udp_socket.recvfrom(1024)
    transmit_time = decode_message(msg)
    local_time = datetime.datetime.utcnow()
    print(f'Current local UTC-time: {local_time}')
    print(f'Current time server UTC-time: {transmit_time}')
    max_time = max([local_time, transmit_time])
    min_time = min([local_time, transmit_time])
    print(f'The time diff is {max_time - min_time}')


if __name__ == '__main__':
    main()

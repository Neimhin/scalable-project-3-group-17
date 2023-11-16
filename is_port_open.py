import asyncio
async def is_port_open(host, port, timeout=0.5):
    conn = asyncio.open_connection(host, port)
    try:
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except asyncio.TimeoutError:
        return False
    except ConnectionRefusedError:
        print(f"connection refused: {host}:{port}")
        return False
    except Exception as e:
        print(f"Error checking port {port} on {host}: {e}")
        return False

if __name__ == "__main__":
        import sys
        print(asyncio.run(is_port_open(sys.argv[1],int(sys.argv[2]))))

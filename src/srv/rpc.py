import uuid

import aiohttp
from solders.hash import Hash
from solders.keypair import Keypair

from config.toml import AppConfig


async def last_transaction(
    keypair: Keypair,
    config: AppConfig,
    session: aiohttp.ClientSession,
) -> list[dict[str, str | bool]]:
    signature = await _latest_signature(keypair, config, session)
    response = await session.post(
        config.app().rpc(),
        json={
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0",
            "method": "getTransaction",
            "params": [
                signature,
                "jsonParsed",
            ],
        },
    )
    json_body = await response.json()
    prepared = [
        account
        for account in json_body["result"]["transaction"]["message"]["accountKeys"]
        if all((
            "ComputeBudget" not in account["pubkey"],
            "turbo" not in account["pubkey"],
            str(keypair.pubkey()) not in account["pubkey"],
            "Sysvar" not in account["pubkey"],
            "9FXCusMeR26k1LkDixLF2dw1AnBX8SsB2cspSSi3BcKE" not in account["pubkey"],
        ))
    ]
    return sorted(prepared, key=lambda x: x["writable"] == True)

async def _latest_signature(
    keypair: Keypair,
    config: AppConfig,
    session: aiohttp.ClientSession,
) -> str:
    response = await session.post(
        config.app().rpc(),
        json={
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0",
            "method": "getSignaturesForAddress",
            "params": [
                str(keypair.pubkey()),
                {
                    "limit": 1,
                },
            ],
        },
    )
    return (await response.json())["result"][0]["signature"]


async def recent_blockhash(
    config: AppConfig,
    session: aiohttp.ClientSession,
) -> Hash:
    response = await session.post(
        config.app().rpc(),
        json={
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0",
            "method": "getLatestBlockhash",
            "params": [{
                "commitment": "finalized",
            }],
        },
    )
    return Hash.from_string(
        (await response.json())["result"]["value"]["blockhash"],
    )


async def send_transaction(
    tx: str,
    config: AppConfig,
    session: aiohttp.ClientSession,
) -> None:
    response = await session.post(
        config.app().rpc(),
        json={
            "id": str(uuid.uuid4()),
            "jsonrpc": "2.0",
            "method": "sendTransaction",
            "params": [
                tx,
                {
                    "encoding": "base64",
                    "maxRetries": 1,
                    "preflightCommitment": "confirmed"
                },
            ],
        },
    )
    return (await response.json())["result"]

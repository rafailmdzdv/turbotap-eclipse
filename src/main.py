import asyncio
import base64
import json
import random
import string
from itertools import batched

import aiohttp
from aiopath import Path
from solders.instruction import AccountMeta, Instruction
from solders.transaction import Transaction
from solders.message import Message
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from structlog import get_logger
from structlog.types import BindableLogger

from config.toml import AppConfig
from exceptions.proxy import ProxyError
from srv import rpc


async def main() -> None:
    logger = get_logger()
    root = Path(__file__).parent.parent
    config = AppConfig()
    wallets = tuple(
        json.loads(private)
        for private in (await (root / "wallets.txt").read_text()).split("\n")
        if private
    )
    proxies = tuple(
        proxy
        for proxy in (await (root / "proxies.txt").read_text()).split("\n")
        if proxy
    )
    batched_proxies = batched(proxies, len(proxies) // len(wallets))
    tasks = [
        asyncio.create_task(process(wallet, list(wal_proxies), config, logger))
        for wallet, wal_proxies in zip(wallets, batched_proxies)
    ]
    await asyncio.gather(*tasks)


async def process(
    wallet: list[int],
    proxies: list[str],
    config: AppConfig,
    logger: BindableLogger,
) -> None:
    proxies = proxies.copy()
    keypair = Keypair.from_bytes(wallet)
    await logger.ainfo("[{0}] Processing account...".format(keypair.pubkey()))
    for proxy in proxies:
        proxies.remove(proxy)
        while True:
            async with aiohttp.ClientSession(
                headers={"user-agent": config.app().user_agent()},
                proxy=proxy,
            ) as session:
                try:
                    await start_loop(keypair, config, session, logger)
                except ProxyError:
                    await logger.aerror(
                        "[{0}] Proxy error ({1}). Switching...".format(
                            keypair.pubkey(),
                            proxy,
                        ),
                    )
                    break
            await logger.ainfo(
                "[{0}] Finished loop. Sleeping for {1}-{2} secs....".format(
                    keypair.pubkey(),
                    config.user().delay_between_loop_start(),
                    config.user().delay_between_loop_end(),
                ),
            )
            await asyncio.sleep(
                random.randint(
                    config.user().delay_between_loop_start(),
                    config.user().delay_between_loop_end(),
                ),
            )
    if not proxies:
        await logger.awarning(
            "[{0}] Not enough proxies".format(keypair.pubkey()),
        )


async def start_loop(
    keypair: Keypair,
    config: AppConfig,
    session: aiohttp.ClientSession,
    logger: BindableLogger,
) -> None:
    for num_click in range(config.user().clicks_per_loop()):
        try:
            message = Message(
                await instructions(keypair, config, session),
                keypair.pubkey(),
            )
            await tap(keypair, message, config, session, logger)
        except (
            aiohttp.ClientProxyConnectionError,
            aiohttp.ClientHttpProxyError,
        ) as _err:
            raise ProxyError from _err
        if num_click == config.user().clicks_per_loop() - 1:
            break
        sleeping_time = random.uniform(
            config.user().clicks_delay_from(),
            config.user().clicks_delay_to(),
        )
        await logger.ainfo(
            "[{0}] Sleeping for {1} secs".format(
                keypair.pubkey(),
                sleeping_time,
            ),
        )
        await asyncio.sleep(sleeping_time)



async def instructions(
    keypair: Keypair,
    config: AppConfig,
    session: aiohttp.ClientSession,
) -> tuple[Instruction, Instruction]:
    acc_keys = await rpc.last_transaction(keypair, config, session)
    ix1 = Instruction(Pubkey.from_string("ComputeBudget111111111111111111111111111111"), b"\x02\xb8\x88\x00\x00", [])
    ix2 = Instruction(
        Pubkey.from_string("turboe9kMc3mSR8BosPkVzoHUfn5RVNzZhkrT2hdGxN"),
        b"\x0b\x93\xb3\xb2\x91v-\xba" + random.choice(string.punctuation + string.ascii_uppercase).encode("utf-8"),
        [
            AccountMeta(
                Pubkey.from_string(acc_keys[0]["pubkey"]),
                False,
                False,
            ),
            AccountMeta(
                Pubkey.from_string(acc_keys[-1]["pubkey"]),
                False,
                True,
            ),
            AccountMeta(Pubkey.from_string("9FXCusMeR26k1LkDixLF2dw1AnBX8SsB2cspSSi3BcKE"), False, False),
            AccountMeta(keypair.pubkey(), True, True),
            AccountMeta(Pubkey.from_string("Sysvar1nstructions1111111111111111111111111"), False, False),
        ],
    )
    return ix1, ix2


async def tap(
    keypair: Keypair,
    message: Message,
    config: AppConfig,
    session: aiohttp.ClientSession,
    logger: BindableLogger,
) -> None:
    tx = Transaction(
        [keypair],
        message,
        await rpc.recent_blockhash(config, session),
    )
    tx_base = base64.b64encode(bytes(tx)).decode("utf-8")
    signature = await rpc.send_transaction(tx_base, config, session)
    await logger.ainfo(
        "[{0}] Clicked, https://eclipsescan.xyz/tx/{1}".format(
            keypair.pubkey(),
            signature,
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())

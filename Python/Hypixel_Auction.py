import asyncio
import aiohttp
from discord_webhook import DiscordWebhook, DiscordEmbed

auction_listings = []

async def get_auction_data(api_key, session):
    url = f"https://api.hypixel.net/skyblock/auctions?key={api_key}"
    async with session.get(url) as response:
        data = await response.json()
        return data

def check_new_auction(new_auction_data, old_auction_data):
    for new_auction in new_auction_data["auctions"]:
        if new_auction not in old_auction_data:
            return new_auction
    return None

def check_auction_update(new_auction_data, old_auction_data):
    for new_auction in new_auction_data["auctions"]:
        for old_auction in old_auction_data:
            if new_auction["uuid"] == old_auction["uuid"] and (new_auction["highest_bid_amount"] != old_auction["highest_bid_amount"] or new_auction["status"] != old_auction["status"]):
                return new_auction
    return None

def send_new_auction_embed(webhook_url, auction):
    try:
        item_id = auction['item_id']
    except KeyError:
        item_id = None
    embed = DiscordEmbed(title=f"New Auction: {auction['item_name']}", color=242424)
    if 'seller' in auction:
        embed.set_author(name=f"Listed by {auction['seller']}")
    embed.add_embed_field(name="Price", value=f"Starting Price: {auction['start']} coins")
    embed.add_embed_field(name="Your Cost", value=f"{auction['starting_bid']} coins")
    embed.add_embed_field(name="Profit", value=f"{auction['start'] - auction['starting_bid']} coins")
    if item_id is not None:
        embed.set_image(url=f"https://sky.lea.moe/{item_id}.png")
    embed.set_footer(text="Powered by Jack-GitHub12", url="https://github.com/Jack-GitHub12")
    webhook = DiscordWebhook(url=webhook_url)
    webhook.add_embed(embed)
    
    response = webhook.execute()

def send_auction_update_embed(webhook_url, auction):
    try:
        item_id = auction['item_id']
    except KeyError:
        item_id = None
    embed = DiscordEmbed(title=f"Auction Update: {auction['item_name']}", color=242424)
    if 'seller' in auction:
        embed.set_author(name=f"Listed by {auction['seller']}")
    embed.add_embed_field(name="Price", value=f"Current Price: {auction['highest_bid_amount']} coins")
    embed.add_embed_field(name="Status", value=auction["status"].capitalize())
    if item_id is not None:
        embed.set_image(url=f"https://sky.lea.moe/{item_id}.png")
    embed.set_footer(text="Powered by Jack-GitHub12", url="https://github.com/Jack-GitHub12")
    webhook = DiscordWebhook(url=webhook_url)
    webhook.add_embed(embed)
    response = webhook.execute()


async def run_task(webhook_url, api_key):
    async with aiohttp.ClientSession() as session:
        new_auction_data = await get_auction_data(api_key, session)
        new_auction = check_new_auction(new_auction_data, auction_listings)
    if new_auction:
        auction_listings.append(new_auction)
    await send_new_auction_embed(webhook_url, new_auction)
    updated_auction = check_auction_update(new_auction_data, auction_listings)
    if updated_auction:
        for i in range(len(auction_listings)):
            if auction_listings[i]["uuid"] == updated_auction["uuid"]:
                auction_listings[i] = updated_auction
    await send_auction_update_embed(webhook_url, updated_auction)

async def main(webhook_url, api_key):
    while True:
        await run_task(webhook_url, api_key)
        await asyncio.sleep(60)
if __name__ == "__main__":
    import os
    webhook_url = os.environ.get("WEBHOOK_URL")
    api_key = os.environ.get("USER_API")
    asyncio.run(main(webhook_url, api_key))


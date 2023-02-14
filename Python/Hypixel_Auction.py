import asyncio
import aiohttp
import discord

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
            if new_auction["uuid"] == old_auction["uuid"] and (new_auction["highest_bid_amount"] != old_auction["highest_bid_amount"] or "status" not in new_auction or new_auction["status"] != old_auction["status"]):
                return new_auction
    return None


async def send_new_auction_embed(webhook, auction):
    embed = discord.Embed(title=f"New Auction: {auction['item_name']}", color=242424)
    if 'seller' in auction:
        embed.set_author(name=f"Listed by {auction['seller']}")
    embed.add_field(name="Price", value=f"Starting Price: {auction['starting_bid']} coins")
    embed.add_field(name="Your Cost", value=f"{auction['starting_bid']} coins")
    embed.add_field(name="Profit", value=f"{auction['starting_bid'] - auction['starting_bid']} coins")
    try:
        item_id = auction['item_id']
        embed.set_thumbnail(url=f"https://sky.shiiyu.moe/skyblock/texture/{item_id}.png")
    except KeyError:
        pass
    embed.set_footer(text="Powered by Jack-GitHub12", icon_url="https://github.com/Jack-GitHub12")
    await webhook.send(embed=embed)

async def send_auction_update_embed(webhook, auction):
    embed = discord.Embed(title=f"Auction Update: {auction['item_name']}", color=242424)
    if 'seller' in auction:
        embed.set_author(name=f"Listed by {auction['seller']}")
    embed.add_field(name="Price", value=f"New Price: {auction['highest_bid_amount']} coins")
    if 'status' in auction:
        embed.add_field(name="Status", value=f"{auction['status']}")
    try:
        item_id = auction['item_id']
        embed.set_thumbnail(url=f"https://sky.shiiyu.moe/skyblock/texture/{item_id}.png")
    except KeyError:
        pass
    embed.set_footer(text="Powered by Jack-GitHub12", icon_url="https://github.com/Jack-GitHub12")
    await webhook.send(embed=embed)



    
async def main():
    api_key = "5e1d10a7-a4de-459f-a94a-aa944ef53300"
    webhook_url = "https://discord.com/api/webhooks/1074838896644464770/s0yJkl2cbRAEwiYjJi9utmMooH-a7oL22ueUVYWYn5YeI8iv3RPFpObCtdRsOwRILsuv"
    interval = 2
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        while True:
            new_auction_data = await get_auction_data(api_key, session)
            new_auction = check_new_auction(new_auction_data, auction_listings)
            if new_auction:
                auction_listings.append(new_auction)
            await send_new_auction_embed(webhook, new_auction)
            auction_update = check_auction_update(new_auction_data, auction_listings)
            if auction_update:
                for i, old_auction in enumerate(auction_listings):
                    if old_auction["uuid"] == auction_update["uuid"]:
                        auction_listings[i] = auction_update
            await send_auction_update_embed(webhook, auction_update)
            await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(main())
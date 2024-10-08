import asyncio
import csv
import time
import random
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, User
from telethon.tl.functions.channels import InviteToChannelRequest  # This import was missing
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError, UserChannelsTooMuchError, PhoneNumberBannedError, UserDeactivatedBanError, ChatAdminRequiredError, UserAlreadyParticipantError

# Your phone and Telegram API credentials
phone = '+919624266638'
api_id = '29463836'
api_hash = '053b0209548e24cf879714efe28dc29f'

async def main_work():
    try:
        async with TelegramClient(phone, api_id, api_hash) as client:
            await client.connect()

            # Ask for authentication if not already authenticated
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                client.sign_in(phone, input('Enter the code: '))

            # Read users from CSV file
            input_file = "members.csv"
            users = []
            with open(input_file, encoding='UTF-8') as f:
                rows = csv.reader(f, delimiter=",", lineterminator="\n")
                next(rows, None)
                for row in rows:
                    user = {
                        'username': row[0],
                        'id': int(row[1]),
                        'access_hash': int(row[2]),
                        'name': row[3]
                    }
                    users.append(user)

            # Retrieve groups and choose one
            chats = []
            last_date = None
            chunk_size = 200
            groups = []

            result = await client(GetDialogsRequest(
                offset_date=last_date,
                offset_id=0,
                offset_peer=InputPeerEmpty(),
                limit=chunk_size,
                hash=0
            ))

            chats.extend(result.chats)

            for chat in chats:
                try:
                    if chat.megagroup == True:
                        groups.append(chat)
                except:
                    continue

            print('Choose a group to add members:')
            for i, group in enumerate(groups):
                print(f'({i}) - {group.title}')

            g_index = input("Enter a Number: ")
            target_group = groups[int(g_index)]
            target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

            # Adding users in bulk
            n = 0
            for user in users:
                n += 1
                if n % 50 == 0:
                    print("Sleeping for 15 minutes after adding 50 users.")
                    time.sleep(900)

                try:
                    if user['username'] != "None":
                        print(f"({n}) Adding {user['username']}")
                    else:
                        print(f"({n}) Adding {user['id']}")

                    if user['username'] != "None":
                        user_to_add = await client.get_entity(user['username'])
                    else:
                        try:
                            user_to_add = await client.get_entity(User(user['id']))
                        except Exception as e:
                            user_to_add = "ERROR"

                    if user_to_add != "ERROR":
                        try:
                            print(f"Waiting for 15-30 Seconds before adding {user['username']}...")
                            time.sleep(random.randrange(15, 30))
                            await client(InviteToChannelRequest(channel=target_group_entity, users=[user_to_add]))  # Fixed
                            print(f"{user['username']} Added or Already in the Group!")
                        except FloodWaitError as e:
                            print(f"Flood wait error: Must wait for {e.seconds} seconds")
                            time.sleep(e.seconds)
                        except PeerFloodError:
                            print("Too many requests. Stopping script to prevent banning.")
                            open("PeerFloodError.txt", 'a+', encoding='utf-8').write(f"{user['username']},{user['id']},{user['access_hash']},{user['name']}\n")
                            time.sleep(600)  # Sleep for 10 minutes to reduce the flood risk
                        except UserChannelsTooMuchError:
                            print(f"{user['username']} is already in too many channels.")
                            open("UserChannelsTooMuchError.txt", 'a+', encoding='utf-8').write(f"{user['username']},{user['id']},{user['access_hash']},{user['name']}\n")
                        except UserPrivacyRestrictedError:
                            print(f"{user['username']}'s privacy settings restrict adding.")
                            open("UserPrivacyRestrictedError.txt", 'a+', encoding='utf-8').write(f"{user['username']},{user['id']},{user['access_hash']},{user['name']}\n")
                        except Exception as e:
                            print(f"Error: {e}")

                    print("Waiting for 15-30 seconds after adding...")
                    time.sleep(random.randrange(15, 30))

                except ValueError as e:
                    print(e)
                    print(f"{user['username']} SKIPPED")

            print("Finished!")

    except PhoneNumberBannedError:
        print("The phone number has been banned.")
    except UserDeactivatedBanError:
        print("The user has been deactivated.")
    except ChatAdminRequiredError:
        print("Chat admin privileges are required.")
    except Exception as e:
        print(e)

asyncio.run(main_work())


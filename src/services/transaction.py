import json

from google import genai
from google.genai import types

from db.models import Category
from repositories import CategoryRepository, RoomRepository
from schemas.transaction import Transaction as TransactionDraft
from settings import Settings


async def build_transaction_draft(
    message: str,
    created_by_id: int,
) -> tuple[TransactionDraft, dict[int, str]]:
    categories = await CategoryRepository().find_all(columns=[Category.id, Category.name])
    rooms = await RoomRepository().get_rooms_with_members_for_user(created_by_id)

    users_map: dict[int, str] = {}
    rooms_context = []
    for room in rooms:
        members = []
        for member in room.members:
            users_map[member.user_id] = member.user.name
            members.append({"user_id": member.user_id, "name": member.user.name})
        rooms_context.append(
            {
                "room_id": room.id,
                "name": room.name,
                "members": members,
            }
        )
    categories_context = [{"id": category_id, "name": category_name} for category_id, category_name in categories]

    prompt = f"""Parse the following expense message into a structured transaction.

User message: {message}

Available categories:
{json.dumps(categories_context, ensure_ascii=False)}

User's rooms and members (use user_id values in payments and splits):
{json.dumps(rooms_context, ensure_ascii=False)}

Rules:
- Set created_by_id to {created_by_id}
- Match category_id from the categories list when possible, otherwise null
- Set room_id to the matching room, or the only room if the user has one room
- payments must account for the full total_amount
- If splits are not specified, split the total equally among all room members
- Use the same language as the input for the description
"""

    client = genai.Client(api_key=Settings().gemini_api_key)
    draft = TransactionDraft.model_validate_json(
        client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=TransactionDraft.model_json_schema(),
            )
        ).text
    )
    draft.created_by_id = created_by_id

    return draft, users_map

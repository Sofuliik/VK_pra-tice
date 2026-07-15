import json
import time
import requests

from config import TOKEN, GROUP_SCREEN_NAME, API_VERSION, TARGET_POSTS_COUNT

API_URL = "https://api.vk.com/method"


def resolve_group_id(screen_name: str) -> int:
    resp = requests.get(
        f"{API_URL}/utils.resolveScreenName",
        params={
            "access_token": TOKEN,
            "v": API_VERSION,
            "screen_name": screen_name,
        },
    )
    data = resp.json()

    if "error" in data:
        raise RuntimeError(f"Ошибка VK при резолве паблика: {data['error']['error_msg']}")

    result = data.get("response")
    if not result or result.get("type") not in ("group", "page"):
        raise RuntimeError(f"Не удалось найти паблик '{screen_name}' или это не группа")

    return result["object_id"]


def get_wall_page(owner_id: int, offset: int, count: int = 100) -> list:
    resp = requests.get(
        f"{API_URL}/wall.get",
        params={
            "access_token": TOKEN,
            "v": API_VERSION,
            "owner_id": owner_id,   
            "count": count,
            "offset": offset,
        },
    )
    data = resp.json()

    if "error" in data:
        raise RuntimeError(f"Ошибка VK: {data['error']['error_msg']}")

    return data["response"]["items"]


def extract_text(post: dict) -> str:
    text = post.get("text", "").strip()
    if text:
        return text

    copy_history = post.get("copy_history")
    if copy_history:
        original_text = copy_history[0].get("text", "").strip()
        return original_text

    return ""


def main():
    print("Ищу паблик по имени...")
    group_id = resolve_group_id(GROUP_SCREEN_NAME)
    owner_id = -group_id  # у пабликов owner_id отрицательный
    print(f"Найден паблик, id = {group_id} (owner_id = {owner_id})")

    collected = []
    offset = 0
    page_size = 100

    while len(collected) < TARGET_POSTS_COUNT:
        posts = get_wall_page(owner_id, offset, page_size)

        if not posts:
            print("Посты закончились раньше, чем набрали нужное количество.")
            break

        for post in posts:
            text = extract_text(post)
            if not text:
                continue  

            collected.append({
                "id": post["id"],
                "text": text,
                "date": post["date"],
                "link": f"https://vk.com/wall{owner_id}_{post['id']}",
            })

        offset += page_size
        print(f"Обработано постов: {offset}, собрано текстовых: {len(collected)}")

        time.sleep(0.35)  

    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(collected, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! Сохранено {len(collected)} постов в posts.json")
    if len(collected) < 5000:
        print("Внимание: собрано меньше 5000 постов — по требованиям кейса нужно больше.")


if __name__ == "__main__":
    main()
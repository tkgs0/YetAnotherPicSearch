from PicImageSearch import AsyncSauceNAO, NetWork

from .ascii2d import ascii2d_search
from .config import config
from .utils import get_source, handle_img


async def saucenao_search(url: str, mode: str, proxy: str, hide_img: bool) -> str:
    saucenao_db = {"all": 999, "pixiv": 5, "danbooru": 9, "anime": 21, "doujin": 38}
    async with NetWork(proxy=proxy) as client:
        saucenao = AsyncSauceNAO(
            client=client, api_key=config.saucenao_api_key, db=saucenao_db[mode]
        )
        res = await saucenao.search(url)
        final_res = ""
        if res is not None:
            res_list = [
                f"SauceNAO（{res.raw[0].similarity}%）\n",
                f"{await handle_img(res.raw[0].thumbnail, proxy, hide_img)}\n",
                f"{res.raw[0].origin['data'].get('jp_name') if mode == 'doujin' else res.raw[0].title}\n",
                f"Author：{res.raw[0].author if res.raw[0].author else ''}\n",
                f"{res.raw[0].url}\n",
                f"Source：{await get_source(res.raw[0].url, proxy)}",
            ]
            for i in res_list:
                if i not in ["\n", "Author：\n"]:
                    final_res += i
            if (
                config.use_ascii2d_when_low_acc
                and res.raw[0].similarity < config.saucenao_low_acc
            ):
                final_res += (
                    f"\n\n相似度 {res.raw[0].similarity}% 过低，自动使用 Ascii2D 进行搜索\n\n"
                )
                final_res += await ascii2d_search(url, proxy, hide_img)
        else:
            final_res = "SauceNAO 暂时无法使用，自动使用 Ascii2D 进行搜索\n\n" + await ascii2d_search(
                url, proxy, hide_img
            )
        return final_res

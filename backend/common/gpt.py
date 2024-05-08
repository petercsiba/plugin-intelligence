from gpt_form_filler.openai_client import CacheStoreBase, PromptCacheEntry
from peewee import InterfaceError

from supabase.models.models import BasePromptLog


class InDatabaseCacheStorage(CacheStoreBase):
    def get_or_create(self, prompt: str, model: str) -> PromptCacheEntry:
        pce = PromptCacheEntry(
            prompt=prompt,
            model=model,
        )

        prompt_hash = pce.prompt_hash()
        try:
            cached_prompt_log: BasePromptLog = BasePromptLog.get(
                BasePromptLog.prompt_hash == prompt_hash, BasePromptLog.model == model
            )
        except BasePromptLog.DoesNotExist:
            return pce
        except InterfaceError:
            print("DB NOT connected, NOT using gpt prompt caching")
            return pce

        pce.result = cached_prompt_log.result
        pce.prompt_tokens = cached_prompt_log.prompt_tokens
        pce.completion_tokens = cached_prompt_log.completion_tokens
        pce.request_time_ms = cached_prompt_log.request_time_ms
        return pce

    def write_cache(self, pce: PromptCacheEntry) -> None:
        cached_prompt_log = BasePromptLog(
            model=pce.model,
            prompt=pce.prompt,
            prompt_hash=pce.prompt_hash(),
            result=pce.result,
            prompt_tokens=pce.prompt_tokens,
            completion_tokens=pce.completion_tokens,
            request_time_ms=pce.request_time_ms,
        )

        try:
            cached_prompt_log.save()
            print(
                f"prompt_log: written to cache {cached_prompt_log.model}:{cached_prompt_log.prompt_hash}"
            )
        # TODO(P3, reliability): There is an edge case when two threads run the same prompt
        except InterfaceError:
            print("DB NOT connected, NOT using gpt prompt caching")

from modules.api.client import RemnaAPI

class InboundAPI:
    """API methods for inbound management (v208 via config profiles)"""
    
    @staticmethod
    async def get_inbounds():
        """Get all inbounds across all config profiles"""
        # v208 exposes inbounds via config profiles
        result = await RemnaAPI.get("config-profiles/inbounds")
        # API returns { response: { total, inbounds: [...] } } which client unwraps to response
        # Our RemnaAPI already returns json['response'] when present
        if isinstance(result, dict) and 'inbounds' in result:
            return result['inbounds']
        return result
    
    @staticmethod
    async def get_full_inbounds():
        """Get inbounds with full details (same as get_inbounds in v208)"""
        return await InboundAPI.get_inbounds()
    
    @staticmethod
    async def add_inbound_to_users(_inbound_uuid):
        """Not supported in v208 (users no longer manage inbounds directly)"""
        return None
    
    @staticmethod
    async def remove_inbound_from_users(_inbound_uuid):
        """Not supported in v208 (users no longer manage inbounds directly)"""
        return None
    
    @staticmethod
    async def add_inbound_to_nodes(_inbound_uuid):
        """Not supported in v208 (nodes use config profile activeInbounds)"""
        return None
    
    @staticmethod
    async def remove_inbound_from_nodes(_inbound_uuid):
        """Not supported in v208 (nodes use config profile activeInbounds)"""
        return None

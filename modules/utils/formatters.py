from datetime import datetime

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def safe_edit_message(query, text, reply_markup=None, parse_mode=None):
    """Safely edit message text with error handling for 'Message is not modified'"""
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if "not modified" in error_msg or "message is not modified" in error_msg:
            # Сообщение уже имеет такой же текст, просто отвечаем на callback
            logger.debug("Message content unchanged, skipping update")
            try:
                await query.answer()
            except Exception:
                pass  # Ignore if callback already answered
            return True
        else:
            # Другая ошибка, логируем ее
            logger.error(f"Error editing message: {e}")
            try:
                await query.answer("❌ Ошибка при обновлении сообщения")
            except Exception:
                pass
            return False

def format_bytes(bytes_value):
    """Format bytes to human-readable format"""
    if not bytes_value:
        return "0 B"  # Handle None or empty values
    
    # Если bytes_value строка, попробуем преобразовать в число
    if isinstance(bytes_value, str):
        try:
            bytes_value = float(bytes_value)
        except (ValueError, TypeError):
            return bytes_value  # Если не удалось преобразовать, возвращаем как есть
    
    if bytes_value == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def escape_markdown(text):
    """Escape Markdown special characters for Telegram (simplified for text, not URLs)"""
    if text is None:
        return ""
    
    text = str(text)
    
    # Упрощенное экранирование только основных символов для обычного текста
    escape_chars = [
        ('\\', '\\\\'),  # Backslash должен быть первым
        ('_', '\\_'),
        ('*', '\\*'),
        ('[', '\\['),
        (']', '\\]'),
        ('`', '\\`')
    ]
    
    for char, escaped in escape_chars:
        text = text.replace(char, escaped)
    
    return text

def format_user_details(user):
    """Format user details for display with enhanced error handling"""
    try:
        # Форматирование даты истечения
        expire_date = datetime.fromisoformat(user['expireAt'].replace('Z', '+00:00'))
        days_left = (expire_date - datetime.now().astimezone()).days
        expire_status = "🟢" if days_left > 7 else "🟡" if days_left > 0 else "🔴"
        expire_text = f"{user['expireAt'][:10]} ({days_left} дней)"
    except Exception as e:
        expire_status = "📅"
        expire_text = user['expireAt'][:10] if 'expireAt' in user and user['expireAt'] else "Не указано"
    
    # Форматирование статуса
    status_emoji = "✅" if user["status"] == "ACTIVE" else "❌"
    
    try:
        message = f"👤 *Пользователь:* {escape_markdown(user.get('username',''))}\n"
        message += f"🆔 *UUID:* `{user.get('uuid','')}`\n"
        if user.get('shortUuid'):
            message += f"🔑 *Короткий UUID:* `{user.get('shortUuid')}`\n"
        if user.get('subscriptionUuid'):
            message += f"📝 *UUID подписки:* `{user.get('subscriptionUuid')}`\n"
        message += "\n"
        
        # Безопасно форматируем URL подписки
        subscription_url = user.get('subscriptionUrl', '')
        if subscription_url:
            # Используем блок кода Markdown для безопасного отображения URL
            safe_url = escape_markdown(subscription_url)
            message += f"🔗 *URL подписки:*\n`{safe_url}`\n\n"
        else:
            message += f"🔗 *URL подписки:* Не указан\n\n"
        
        message += f"📊 *Статус:* {status_emoji} {user['status']}\n"
        message += f"📈 *Трафик:* {format_bytes(user['usedTrafficBytes'])}/{format_bytes(user['trafficLimitBytes'])}\n"
        message += f"🔄 *Стратегия сброса:* {user['trafficLimitStrategy']}\n"
        message += f"{expire_status} *Истекает:* {expire_text}\n\n"
        
        if user.get('description'):
            message += f"📝 *Описание:* {escape_markdown(str(user['description']))}\n"
        
        if user.get('tag'):
            message += f"🏷️ *Тег:* {escape_markdown(str(user['tag']))}\n"
        
        if user.get('telegramId'):
            message += f"📱 *Telegram ID:* {user['telegramId']}\n"
        
        if user.get('email'):
            message += f"📧 *Email:* {escape_markdown(str(user['email']))}\n"
        
        if user.get('hwidDeviceLimit'):
            message += f"📱 *Лимит устройств:* {user['hwidDeviceLimit']}\n"
        
        if user.get('createdAt'):
            message += f"\n⏱️ *Создан:* {user['createdAt'][:10]}\n"
        if user.get('updatedAt'):
            message += f"🔄 *Обновлен:* {user['updatedAt'][:10]}\n"
        
        return message
    except Exception as e:
        # Fallback форматирование без Markdown
        logger.warning(f"Error in format_user_details: {e}")
        
        message = f"👤 Пользователь: {user.get('username','')}\n"
        message += f"🆔 UUID: {user.get('uuid','')}\n"
        if user.get('shortUuid'):
            message += f"🔑 Короткий UUID: {user.get('shortUuid')}\n"
        if user.get('subscriptionUuid'):
            message += f"📝 UUID подписки: {user.get('subscriptionUuid')}\n\n"
        
        # Добавляем URL подписки в fallback без форматирования
        subscription_url = user.get('subscriptionUrl', '')
        if subscription_url:
            message += f"🔗 URL подписки:\n{subscription_url}\n\n"
        else:
            message += f"🔗 URL подписки: Не указан\n\n"
        
        message += f"📊 Статус: {status_emoji} {user['status']}\n"
        message += f"📈 Трафик: {format_bytes(user['usedTrafficBytes'])}/{format_bytes(user['trafficLimitBytes'])}\n"
        message += f"🔄 Стратегия сброса: {user['trafficLimitStrategy']}\n"
        message += f"{expire_status} Истекает: {expire_text}\n\n"
        
        if user.get('description'):
            message += f"📝 Описание: {user['description']}\n"
        
        if user.get('tag'):
            message += f"🏷️ Тег: {user['tag']}\n"
        
        if user.get('telegramId'):
            message += f"📱 Telegram ID: {user['telegramId']}\n"
        
        if user.get('email'):
            message += f"📧 Email: {user['email']}\n"
        
        if user.get('hwidDeviceLimit'):
            message += f"📱 Лимит устройств: {user['hwidDeviceLimit']}\n"
        
        if user.get('createdAt'):
            message += f"\n⏱️ Создан: {user['createdAt'][:10]}\n"
        if user.get('updatedAt'):
            message += f"🔄 Обновлен: {user['updatedAt'][:10]}\n"
        
        return message

def format_user_details_safe(user):
    """Format user details for display without Markdown (safe fallback)"""
    try:
        # Форматирование даты истечения
        expire_date = datetime.fromisoformat(user['expireAt'].replace('Z', '+00:00'))
        days_left = (expire_date - datetime.now().astimezone()).days
        expire_status = "🟢" if days_left > 7 else "🟡" if days_left > 0 else "🔴"
        expire_text = f"{user['expireAt'][:10]} ({days_left} дней)"
    except Exception as e:
        expire_status = "📅"
        expire_text = user['expireAt'][:10] if 'expireAt' in user and user['expireAt'] else "Не указано"
    
    # Форматирование статуса
    status_emoji = "✅" if user["status"] == "ACTIVE" else "❌"
    
    message = f"👤 Пользователь: {user['username']}\n"
    message += f"🆔 UUID: {user.get('uuid','')}\n"
    if user.get('shortUuid'):
        message += f"🔑 Короткий UUID: {user.get('shortUuid')}\n"
    if user.get('subscriptionUuid'):
        message += f"📝 UUID подписки: {user.get('subscriptionUuid')}\n\n"
    
    # URL подписки без какого-либо форматирования (без <pre> и без блоков кода)
    subscription_url = user.get('subscriptionUrl', '')
    if subscription_url:
        message += f"🔗 URL подписки:\n{subscription_url}\n\n"
    else:
        message += f"🔗 URL подписки: Не указан\n\n"
    
    message += f"📊 Статус: {status_emoji} {user['status']}\n"
    message += f"📈 Трафик: {format_bytes(user['usedTrafficBytes'])}/{format_bytes(user['trafficLimitBytes'])}\n"
    message += f"🔄 Стратегия сброса: {user['trafficLimitStrategy']}\n"
    message += f"{expire_status} Истекает: {expire_text}\n\n"
    
    if user.get('description'):
        message += f"📝 Описание: {user['description']}\n"
    
    if user.get('tag'):
        message += f"🏷️ Тег: {user['tag']}\n"
    
    if user.get('telegramId'):
        message += f"📱 Telegram ID: {user['telegramId']}\n"
    
    if user.get('email'):
        message += f"📧 Email: {user['email']}\n"
    
    if user.get('hwidDeviceLimit'):
        message += f"📱 Лимит устройств: {user['hwidDeviceLimit']}\n"
    
    if user.get('createdAt'):
        message += f"\n⏱️ Создан: {user['createdAt'][:10]}\n"
    if user.get('updatedAt'):
        message += f"🔄 Обновлен: {user['updatedAt'][:10]}\n"
    
    return message

def format_node_details(node):
    """Format node details for display"""
    status_emoji = "🟢" if node["isConnected"] and not node["isDisabled"] else "🔴"

    message = f"*Информация о сервере*\n\n"
    message += f"{status_emoji} *Имя*: {escape_markdown(node['name'])}\n"
    message += f"🆔 *UUID*: `{node['uuid']}`\n"
    message += f"🌐 *Адрес*: {escape_markdown(node['address'])}:{node['port']}\n\n"

    message += f"📊 *Статус*:\n"
    message += f"  • Подключен: {'✅' if node['isConnected'] else '❌'}\n"
    message += f"  • Отключен: {'✅' if node['isDisabled'] else '❌'}\n"
    message += f"  • Онлайн: {'✅' if node['isNodeOnline'] else '❌'}\n"
    message += f"  • Xray запущен: {'✅' if node['isXrayRunning'] else '❌'}\n\n"

    if node.get("xrayVersion"):
        message += f"📦 *Версия Xray*: {escape_markdown(node['xrayVersion'])}\n"

    message += f"⏱️ *Uptime*: {escape_markdown(node['xrayUptime'])}\n"
    
    message += f"🌍 *Страна*: {node['countryCode']}\n"
    message += f"📊 *Множитель потребления*: {node['consumptionMultiplier']}x\n\n"

    if node.get("trafficLimitBytes") is not None:
        message += f"📈 *Трафик*: {format_bytes(node['trafficUsedBytes'])}/{format_bytes(node['trafficLimitBytes'])}\n"

    if node.get("usersOnline") is not None:
        message += f"👥 *Пользователей онлайн*: {node['usersOnline']}\n"

    if node.get("cpuCount") and node.get("cpuModel"):
        message += f"\n💻 *Система*:\n"
        message += f"  • CPU: {escape_markdown(node['cpuModel'])} ({node['cpuCount']} ядер)\n"
        if node.get("totalRam"):
            message += f"  • RAM: {escape_markdown(node['totalRam'])}\n"

    return message

def format_host_details(host):
    """Format host details for display"""
    status_emoji = "🟢" if not host["isDisabled"] else "🔴"

    message = f"*Информация о хосте*\n\n"
    message += f"{status_emoji} *Название*: {escape_markdown(host['remark'])}\n"
    message += f"🆔 *UUID*: `{host['uuid']}`\n"
    message += f"🌐 *Адрес*: {escape_markdown(host['address'])}:{host['port']}\n\n"
    
    # v208: inbound is an object with configProfileUuid/configProfileInboundUuid
    inbound = host.get('inbound') or {}
    config_profile_uuid = inbound.get('configProfileUuid')
    config_profile_inbound_uuid = inbound.get('configProfileInboundUuid')
    if config_profile_uuid or config_profile_inbound_uuid:
        cp = config_profile_uuid or '—'
        cpi = config_profile_inbound_uuid or '—'
        message += f"🔌 *Inbound*: cp=`{cp}` inbound=`{cpi}`\n"
    
    if host.get("path"):
        message += f"🛣️ *Путь*: {escape_markdown(host['path'])}\n"
    
    if host.get("sni"):
        message += f"🔒 *SNI*: {escape_markdown(host['sni'])}\n"
    
    if host.get("host"):
        message += f"🏠 *Host*: {escape_markdown(host['host'])}\n"
    
    if host.get("alpn"):
        message += f"🔄 *ALPN*: {escape_markdown(host['alpn'])}\n"
    
    if host.get("fingerprint"):
        message += f"👆 *Fingerprint*: {escape_markdown(host['fingerprint'])}\n"
    
    # allowInsecure removed in v208; keep Security Layer
    message += f"🛡️ *Security Layer*: {host.get('securityLayer', 'DEFAULT')}\n"
    
    return message

def format_system_stats(stats):
    """Format system statistics for display"""
    message = f"*Статистика системы*\n\n"

    # CPU and Memory
    message += f"💻 *CPU*: {stats['cpu']['cores']} ядер ({stats['cpu']['physicalCores']} физических)\n"

    total_mem = format_bytes(stats['memory']['total'])
    used_mem = format_bytes(stats['memory']['used'])
    free_mem = format_bytes(stats['memory']['free'])

    message += f"🧠 *Память*: {used_mem} из {total_mem} (свободно: {free_mem})\n"

    # Uptime
    uptime_days = stats['uptime'] // (24 * 3600)
    uptime_hours = (stats['uptime'] % (24 * 3600)) // 3600
    uptime_minutes = (stats['uptime'] % 3600) // 60

    message += f"⏱️ *Uptime*: {uptime_days}д {uptime_hours}ч {uptime_minutes}м\n\n"

    # Users
    message += f"👥 *Пользователи*:\n"
    message += f"  • Всего: {stats['users']['totalUsers']}\n"

    if 'statusCounts' in stats['users']:
        for status, count in stats['users']['statusCounts'].items():
            status_emoji = "✅" if status == "ACTIVE" else "❌"
            message += f"  • {status_emoji} {status}: {count}\n"

    # Преобразуем totalTrafficBytes в число, если это строка
    total_traffic = stats['users'].get('totalTrafficBytes', 0)
    message += f"  • Общий трафик: {format_bytes(total_traffic)}\n\n"

    # Online stats
    message += f"📊 *Онлайн статистика*:\n"
    message += f"  • Сейчас онлайн: {stats['onlineStats']['onlineNow']}\n"
    message += f"  • За последний день: {stats['onlineStats']['lastDay']}\n"
    message += f"  • За последнюю неделю: {stats['onlineStats']['lastWeek']}\n"
    message += f"  • Никогда не были онлайн: {stats['onlineStats']['neverOnline']}\n"

    return message

def format_bandwidth_stats(stats):
    """Format bandwidth statistics for display"""
    message = f"*Статистика трафика*\n\n"

    message += f"📅 *За последние 2 дня*:\n"
    message += f"  • Текущий: {stats['bandwidthLastTwoDays']['current']}\n"
    message += f"  • Предыдущий: {stats['bandwidthLastTwoDays']['previous']}\n"
    message += f"  • Разница: {stats['bandwidthLastTwoDays']['difference']}\n\n"

    message += f"📆 *За последние 7 дней*:\n"
    message += f"  • Текущий: {stats['bandwidthLastSevenDays']['current']}\n"
    message += f"  • Предыдущий: {stats['bandwidthLastSevenDays']['previous']}\n"
    message += f"  • Разница: {stats['bandwidthLastSevenDays']['difference']}\n\n"

    message += f"📊 *За последние 30 дней*:\n"
    message += f"  • Текущий: {stats['bandwidthLast30Days']['current']}\n"
    message += f"  • Предыдущий: {stats['bandwidthLast30Days']['previous']}\n"
    message += f"  • Разница: {stats['bandwidthLast30Days']['difference']}\n\n"

    message += f"📈 *За текущий месяц*:\n"
    message += f"  • Текущий: {stats['bandwidthCalendarMonth']['current']}\n"
    message += f"  • Предыдущий: {stats['bandwidthCalendarMonth']['previous']}\n"
    message += f"  • Разница: {stats['bandwidthCalendarMonth']['difference']}\n\n"

    message += f"📉 *За текущий год*:\n"
    message += f"  • Текущий: {stats['bandwidthCurrentYear']['current']}\n"
    message += f"  • Предыдущий: {stats['bandwidthCurrentYear']['previous']}\n"
    message += f"  • Разница: {stats['bandwidthCurrentYear']['difference']}\n"

    return message

def format_inbound_details(inbound):
    """Format inbound details for display"""
    message = f"*Информация об Inbound*\n\n"
    message += f"🏷️ *Тег*: {escape_markdown(inbound['tag'])}\n"
    message += f"🆔 *UUID*: `{inbound['uuid']}`\n"
    message += f"🔌 *Тип*: {inbound['type']}\n"
    message += f"🔢 *Порт*: {inbound['port']}\n"
    
    if inbound.get('network'):
        message += f"🌐 *Сеть*: {inbound['network']}\n"
    
    if inbound.get('security'):
        message += f"🔒 *Безопасность*: {inbound['security']}\n"
    
    if 'users' in inbound:
        message += f"\n👥 *Пользователи*:\n"
        message += f"  • Активные: {inbound['users']['enabled']}\n"
        message += f"  • Отключенные: {inbound['users']['disabled']}\n"
    
    if 'nodes' in inbound:
        message += f"\n🖥️ *Серверы*:\n"
        message += f"  • Активные: {inbound['nodes']['enabled']}\n"
        message += f"  • Отключенные: {inbound['nodes']['disabled']}\n"
    
    return message

"""
User CRUD Service
Сервис для CRUD операций с пользователями
"""

from typing import Optional, Dict, Any, List
from db.connection import db
from db.queries import users as queries
from utils.logger import logger


class UserCRUD:
    """CRUD операции для пользователей"""
    
    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать нового пользователя
        
        Args:
            user_data: Данные пользователя
            
        Returns:
            Созданный пользователь
        """
        try:
            logger.info(f"Creating user: {user_data.get('username')}")
            result = db.execute_query(queries.INSERT_USER, user_data, fetch=True)
            
            if result and len(result) > 0:
                user_id = result[0]['id']
                logger.info(f"User created with ID: {user_id}, fetching full user data...")
                user = self.get_by_id(user_id)
                if user is None:
                    logger.error(f"Failed to fetch created user with ID: {user_id}")
                    raise Exception(f"User created but could not be retrieved (ID: {user_id})")
                logger.info(f"User {user_id} retrieved successfully")
                return user
            else:
                logger.error(f"INSERT_USER query returned no result")
                raise Exception("Failed to create user - no ID returned")
                
        except Exception as e:
            logger.error(f"Error creating user: {e}", exc_info=True)
            raise
    
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя по ID"""
        try:
            logger.debug(f"Fetching user by ID: {user_id}")
            result = db.execute_query(
                queries.SELECT_USER_BY_ID,
                {'id': user_id},
                fetch=True
            )
            
            if result and len(result) > 0:
                user = dict(result[0])
                # Ensure roles is a list
                if user.get('roles') is None:
                    user['roles'] = []
                logger.debug(f"User {user_id} found: {user.get('username')}")
                return user
            logger.warning(f"User with ID {user_id} not found in database")
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}", exc_info=True)
            return None
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Получить пользователя по username"""
        try:
            result = db.execute_query(
                queries.SELECT_USER_BY_USERNAME,
                {'username': username},
                fetch=True
            )
            
            if result and len(result) > 0:
                user = dict(result[0])
                if user.get('roles') is None:
                    user['roles'] = []
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получить пользователя по email"""
        try:
            result = db.execute_query(
                queries.SELECT_USER_BY_EMAIL,
                {'email': email},
                fetch=True
            )
            
            if result and len(result) > 0:
                user = dict(result[0])
                if user.get('roles') is None:
                    user['roles'] = []
                return user
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def check_exists(self, username: str, email: str) -> Dict[str, bool]:
        """Проверить существование username и email"""
        try:
            result = db.execute_query(
                queries.CHECK_USER_EXISTS,
                {'username': username, 'email': email},
                fetch=True
            )
            
            if result and len(result) > 0:
                return {
                    'username_exists': result[0]['username_exists'],
                    'email_exists': result[0]['email_exists']
                }
            return {'username_exists': False, 'email_exists': False}
            
        except Exception as e:
            logger.error(f"Error checking user exists: {e}")
            return {'username_exists': False, 'email_exists': False}
    
    def update(self, user_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить пользователя"""
        try:
            updates['id'] = user_id
            db.execute_query(queries.UPDATE_USER, updates, fetch=False)
            return self.get_by_id(user_id)
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Обновить пароль пользователя"""
        try:
            db.execute_query(
                queries.UPDATE_PASSWORD,
                {'id': user_id, 'password_hash': password_hash},
                fetch=False
            )
            return True
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False
    
    def delete(self, user_id: int, hard_delete: bool = False) -> bool:
        """Удалить пользователя"""
        try:
            if hard_delete:
                query = queries.DELETE_USER_HARD
            else:
                query = queries.DELETE_USER_SOFT
            
            db.execute_query(query, {'id': user_id}, fetch=False)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        only_active: Optional[bool] = None,
        search_query: Optional[str] = None,
        sort_by: str = 'username',
        sort_order: str = 'ASC'
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        Получить список пользователей
        
        Returns:
            Tuple (список пользователей, общее количество)
        """
        try:
            search_pattern = f"%{search_query}%" if search_query else None
            offset = (page - 1) * page_size
            
            params = {
                'only_active': only_active,
                'search_query': search_query,
                'search_pattern': search_pattern,
                'sort_by': sort_by,
                'sort_order': sort_order,
                'page_size': page_size,
                'offset': offset
            }
            
            # Get users
            users = db.execute_query(queries.LIST_USERS, params, fetch=True)
            
            # Get total count
            count_params = {
                'only_active': only_active,
                'search_query': search_query,
                'search_pattern': search_pattern
            }
            count_result = db.execute_query(queries.COUNT_USERS, count_params, fetch=True)
            total = count_result[0]['total'] if count_result else 0
            
            return [dict(u) for u in users], total
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return [], 0


# Singleton instance
user_crud = UserCRUD()


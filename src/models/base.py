"""
Module contenant la classe de base pour tous les modèles de données.

Cette classe fournit des fonctionnalités communes à tous les modèles,
telles que la conversion en dictionnaire et la création d'instances à partir de dictionnaires.
"""

from typing import Dict, Any, Type, TypeVar, Optional
from datetime import datetime
import logging

# Type variable pour les sous-classes de BaseModel
T = TypeVar('T', bound='BaseModel')

class BaseModel:
    """Classe de base pour tous les modèles de données."""
    
    # Les sous-classes doivent définir ces attributs
    _table_name: str = ''
    _primary_key: str = 'id'
    _fields: Dict[str, type] = {}
    
    def __init__(self, **kwargs):
        """Initialise le modèle avec les valeurs fournies."""
        for field, field_type in self._fields.items():
            value = kwargs.get(field)
            
            # Conversion des types
            if value is not None and field_type:
                try:
                    # Gestion spéciale pour les dates
                    if field_type == datetime and isinstance(value, str):
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    # Conversion du type
                    elif not isinstance(value, field_type):
                        value = field_type(value)
                except (ValueError, TypeError) as e:
                    logging.warning(
                        f"Impossible de convertir {field}={value!r} en {field_type.__name__}: {e}"
                    )
            
            setattr(self, field, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le modèle en dictionnaire.
        
        Returns:
            Un dictionnaire contenant les attributs du modèle.
        """
        result = {}
        for field in self._fields:
            value = getattr(self, field, None)
            
            # Conversion des dates en chaînes ISO
            if isinstance(value, datetime):
                value = value.isoformat()
            # Conversion des sous-modèles en dictionnaires
            elif hasattr(value, 'to_dict'):
                value = value.to_dict()
            
            result[field] = value
        
        return result
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Crée une instance du modèle à partir d'un dictionnaire.
        
        Args:
            data: Dictionnaire contenant les données du modèle.
            
        Returns:
            Une instance du modèle.
        """
        return cls(**data)
    
    def __repr__(self) -> str:
        """Représentation en chaîne du modèle."""
        attrs = []
        for field in self._fields:
            value = getattr(self, field, None)
            if value is not None:
                attrs.append(f"{field}={value!r}")
        
        return f"{self.__class__.__name__}({', '.join(attrs)})
    
    def __eq__(self, other: object) -> bool:
        """Compare deux modèles pour l'égalité."""
        if not isinstance(other, self.__class__):
            return False
            
        for field in self._fields:
            if getattr(self, field) != getattr(other, field):
                return False
                
        return True

"""Centralized hotkeys manager."""
import tkinter as tk
from typing import Dict, List, Tuple, Optional, Callable
from collections import defaultdict


class HotkeyBinding:
    """Class for storing hotkey binding information."""

    def __init__(self, key_combination: str, handler: Callable, component: str, description: str = "", widget: Optional[tk.Widget] = None):
        """
        Initialize binding.

        Args:
            key_combination: Key combination (e.g., "<Control-c>")
            handler: Event handler
            component: Name of component registering the binding
            description: Action description
            widget: Widget the key is bound to (None for root)
        """
        self.key_combination = key_combination
        self.handler = handler
        self.component = component
        self.description = description
        self.widget = widget
        self.bound = False

    def __repr__(self):
        return f"HotkeyBinding({self.key_combination}, {self.component}, {self.description})"


class HotkeyManager:
    """Centralized manager for hotkey management."""

    def __init__(self, root: tk.Widget):
        """
        Initialize hotkey manager.

        Args:
            root: Root widget of the application
        """
        self.root = root
        # Dictionary: key_combination -> list of bindings
        self._bindings: Dict[str, List[HotkeyBinding]] = defaultdict(list)
        # Dictionary for fast lookup by component
        self._component_bindings: Dict[str, List[HotkeyBinding]] = defaultdict(list)

    def register(self, key_combination: str, handler: Callable, component: str, 
                 description: str = "", widget: Optional[tk.Widget] = None, 
                 case_sensitive: bool = False) -> bool:
        """
        Register hotkey.

        Args:
            key_combination: Key combination (e.g., "<Control-c>")
            handler: Event handler
            component: Component name (e.g., "PythonEditor")
            description: Action description for user
            widget: Widget for binding (None for root)
            case_sensitive: Whether to consider key case

        Returns:
            True if successfully registered, False if conflict
        """
        # Check for conflicts
        if key_combination in self._bindings:
            existing = self._bindings[key_combination]
            if existing and not case_sensitive:
                # Warning about potential conflict
                print(f"Warning: Combination {key_combination} is already used by components: {[b.component for b in existing]}")

        # Create wrapper for handler with error logging
        def wrapped_handler(event):
            try:
                return handler(event)
            except Exception as e:
                print(f"Error in hotkey handler {key_combination} (component {component}): {e}")
                return None

        # Create binding
        binding = HotkeyBinding(key_combination, wrapped_handler, component, description, widget)

        # Register
        target_widget = widget if widget else self.root
        target_widget.bind(key_combination, wrapped_handler, add="+")
        binding.bound = True

        # Save in dictionaries
        self._bindings[key_combination].append(binding)
        self._component_bindings[component].append(binding)

        return True

    def register_case_insensitive(self, key_combination: str, handler: Callable, 
                                  component: str, description: str = "", 
                                  widget: Optional[tk.Widget] = None) -> bool:
        """
        Register hotkey with automatic support for both cases.

        Args:
            key_combination: Key combination (e.g., "<Control-c>")
            handler: Event handler
            component: Component name
            description: Action description
            widget: Widget for binding (None for root)

        Returns:
            True if successfully registered
        """
        try:
            from utils.keyboard_utils import bind_case_insensitive
        except ImportError:
            # Fallback if import doesn't work
            bind_case_insensitive = None

        # Create wrapper for handler with error logging
        def wrapped_handler(event):
            try:
                return handler(event)
            except Exception as e:
                print(f"Error in hotkey handler {key_combination} (component {component}): {e}")
                return None

        # Register both variants
        if bind_case_insensitive:
            bind_case_insensitive(widget if widget else self.root, key_combination, wrapped_handler, add="+")
        else:
            # Fallback: register manually
            target_widget = widget if widget else self.root
            # Extract modifiers and key
            if key_combination.startswith("<") and key_combination.endswith(">"):
                parts = key_combination[1:-1].split("-")
                if len(parts) > 1:
                    modifiers = "-".join(parts[:-1])
                    key = parts[-1]
                    target_widget.bind(f"<{modifiers}-{key.lower()}>", wrapped_handler, add="+")
                    target_widget.bind(f"<{modifiers}-{key.upper()}>", wrapped_handler, add="+")
                else:
                    key = parts[0]
                    target_widget.bind(f"<{key.lower()}>", wrapped_handler, add="+")
                    target_widget.bind(f"<{key.upper()}>", wrapped_handler, add="+")

        # Create binding for record (register as single entry)
        binding = HotkeyBinding(key_combination, wrapped_handler, component, description, widget)
        binding.bound = True

        self._bindings[key_combination].append(binding)
        self._component_bindings[component].append(binding)

        return True

    def unregister(self, key_combination: str, component: str) -> bool:
        """
        Unregister hotkey for specific component.

        Args:
            key_combination: Key combination
            component: Component name

        Returns:
            True if successfully unregistered, False if not found
        """
        if key_combination not in self._bindings:
            return False

        # Find bindings for this component
        bindings_to_remove = [b for b in self._bindings[key_combination] if b.component == component]

        if not bindings_to_remove:
            return False

        # Unbind from widget
        for binding in bindings_to_remove:
            target_widget = binding.widget if binding.widget else self.root
            try:
                target_widget.unbind(key_combination)
            except Exception as e:
                print(f"Error unbinding {key_combination}: {e}")

        # Remove from dictionaries
        self._bindings[key_combination] = [b for b in self._bindings[key_combination] if b.component != component]
        if not self._bindings[key_combination]:
            del self._bindings[key_combination]

        self._component_bindings[component] = [b for b in self._component_bindings[component] if b.key_combination != key_combination]

        return True

    def unregister_component(self, component: str) -> int:
        """
        Unregister all bindings for component.

        Args:
            component: Component name

        Returns:
            Number of unregistered bindings
        """
        if component not in self._component_bindings:
            return 0

        bindings = self._component_bindings[component].copy()
        count = 0

        for binding in bindings:
            if self.unregister(binding.key_combination, component):
                count += 1

        return count

    def get_all_bindings(self) -> List[Tuple[str, str, str]]:
        """
        Get list of all bindings.

        Returns:
            List of tuples (key combination, component, description)
        """
        result = []
        for key_combination, bindings in self._bindings.items():
            for binding in bindings:
                result.append((key_combination, binding.component, binding.description))
        return result

    def get_bindings_by_component(self, component: str) -> List[HotkeyBinding]:
        """
        Get all bindings for component.

        Args:
            component: Component name

        Returns:
            List of bindings
        """
        return self._component_bindings.get(component, []).copy()

    def get_bindings_by_key(self, key_combination: str) -> List[HotkeyBinding]:
        """
        Get all bindings for key combination.

        Args:
            key_combination: Key combination

        Returns:
            List of bindings
        """
        return self._bindings.get(key_combination, []).copy()

    def has_conflicts(self) -> List[Tuple[str, List[str]]]:
        """
        Check for conflicts (multiple components on same combination).

        Returns:
            List of tuples (key combination, list of components)
        """
        conflicts = []
        for key_combination, bindings in self._bindings.items():
            if len(bindings) > 1:
                components = [b.component for b in bindings]
                conflicts.append((key_combination, components))
        return conflicts


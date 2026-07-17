import os
import json
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

class GraphStoreInterface:
    """
    Interface for pluggable Knowledge Graph stores.
    """
    def save_node(self, node_id: str, node_type: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def get_nodes(self) -> List[Tuple[str, str, Dict[str, Any]]]:
        """Returns List of (node_id, node_type, data) tuples."""
        raise NotImplementedError()

    def delete_node(self, node_id: str) -> None:
        raise NotImplementedError()

    def save_relationship(self, source_id: str, target_id: str, relation_type: str, data: Dict[str, Any]) -> None:
        raise NotImplementedError()

    def get_relationships(self) -> List[Tuple[str, str, str, Dict[str, Any]]]:
        """Returns List of (source_id, target_id, relation_type, data) tuples."""
        raise NotImplementedError()

    def delete_relationship(self, source_id: str, target_id: str, relation_type: str) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()


class SQLiteGraphStore(GraphStoreInterface):
    """
    SQLite-backed graph persistence store.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    node_id TEXT PRIMARY KEY,
                    node_type TEXT,
                    serialized_data TEXT
                )
            """)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS graph_edges (
                    source_id TEXT,
                    target_id TEXT,
                    relation_type TEXT,
                    serialized_data TEXT,
                    PRIMARY KEY (source_id, target_id, relation_type)
                )
            """)

    def save_node(self, node_id: str, node_type: str, data: Dict[str, Any]) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO graph_nodes (node_id, node_type, serialized_data) VALUES (?, ?, ?)",
                (node_id, node_type, json.dumps(data))
            )

    def get_nodes(self) -> List[Tuple[str, str, Dict[str, Any]]]:
        nodes = []
        cursor = self._conn.execute("SELECT node_id, node_type, serialized_data FROM graph_nodes")
        for row in cursor.fetchall():
            nodes.append((row["node_id"], row["node_type"], json.loads(row["serialized_data"])))
        return nodes

    def delete_node(self, node_id: str) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM graph_nodes WHERE node_id = ?", (node_id,))
            self._conn.execute("DELETE FROM graph_edges WHERE source_id = ? OR target_id = ?", (node_id, node_id))

    def save_relationship(self, source_id: str, target_id: str, relation_type: str, data: Dict[str, Any]) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO graph_edges (source_id, target_id, relation_type, serialized_data)
                VALUES (?, ?, ?, ?)
                """,
                (source_id, target_id, relation_type, json.dumps(data))
            )

    def get_relationships(self) -> List[Tuple[str, str, str, Dict[str, Any]]]:
        edges = []
        cursor = self._conn.execute("SELECT source_id, target_id, relation_type, serialized_data FROM graph_edges")
        for row in cursor.fetchall():
            edges.append((row["source_id"], row["target_id"], row["relation_type"], json.loads(row["serialized_data"])))
        return edges

    def delete_relationship(self, source_id: str, target_id: str, relation_type: str) -> None:
        with self._conn:
            self._conn.execute(
                "DELETE FROM graph_edges WHERE source_id = ? AND target_id = ? AND relation_type = ?",
                (source_id, target_id, relation_type)
            )

    def clear(self) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM graph_nodes")
            self._conn.execute("DELETE FROM graph_edges")

    def close(self) -> None:
        self._conn.close()


class JSONGraphStore(GraphStoreInterface):
    """
    JSON flat-file-backed graph persistence store.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._init_store()

    def _init_store(self) -> None:
        directory = os.path.dirname(os.path.abspath(self.filepath))
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.filepath):
            self._write_raw({"nodes": {}, "edges": []})

    def _read_raw(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"nodes": {}, "edges": []}

    def _write_raw(self, data: Dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_node(self, node_id: str, node_type: str, data: Dict[str, Any]) -> None:
        store = self._read_raw()
        store["nodes"][node_id] = {"node_type": node_type, "data": data}
        self._write_raw(store)

    def get_nodes(self) -> List[Tuple[str, str, Dict[str, Any]]]:
        store = self._read_raw()
        nodes = []
        for nid, val in store["nodes"].items():
            nodes.append((nid, val["node_type"], val["data"]))
        return nodes

    def delete_node(self, node_id: str) -> None:
        store = self._read_raw()
        if node_id in store["nodes"]:
            del store["nodes"][node_id]
        # Delete connected edges
        store["edges"] = [
            edge for edge in store["edges"] 
            if edge["source_id"] != node_id and edge["target_id"] != node_id
        ]
        self._write_raw(store)

    def save_relationship(self, source_id: str, target_id: str, relation_type: str, data: Dict[str, Any]) -> None:
        store = self._read_raw()
        edges_list = store["edges"]
        updated = False
        
        for idx, edge in enumerate(edges_list):
            if (edge["source_id"] == source_id and 
                edge["target_id"] == target_id and 
                edge["relation_type"] == relation_type):
                edges_list[idx]["data"] = data
                updated = True
                break
                
        if not updated:
            edges_list.append({
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": relation_type,
                "data": data
            })
        self._write_raw(store)

    def get_relationships(self) -> List[Tuple[str, str, str, Dict[str, Any]]]:
        store = self._read_raw()
        edges = []
        for edge in store["edges"]:
            edges.append((edge["source_id"], edge["target_id"], edge["relation_type"], edge["data"]))
        return edges

    def delete_relationship(self, source_id: str, target_id: str, relation_type: str) -> None:
        store = self._read_raw()
        store["edges"] = [
            edge for edge in store["edges"]
            if not (edge["source_id"] == source_id and 
                    edge["target_id"] == target_id and 
                    edge["relation_type"] == relation_type)
        ]
        self._write_raw(store)

    def clear(self) -> None:
        self._write_raw({"nodes": {}, "edges": []})

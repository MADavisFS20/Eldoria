package eldoria.core.model

/** Underground dungeon (tunnels/caves) or the sky realm reached by beanstalk. */
enum class RealmKind { DUNGEON, SKY_REALM }

enum class QuestType { RETRIEVE_ARTIFACT, DEFEAT_GUARDIAN, RESCUE_CAPTIVE }

/** One room/chamber (dungeon) or island/terrace (sky realm) inside a SubRealm. */
data class SubRealmRoom(
    val id: String,
    val name: String,
    val description: String,
    val difficultyTier: Int,
    val isBossRoom: Boolean,
    val beings: List<SpawnEntry>,
    val items: List<Item>,
    /** direction ("north","south","east","west","up","down", or a fallback "passage_*") -> room id */
    val exits: Map<String, String>,
)

data class SubRealmQuest(
    val title: String,
    val type: QuestType,
    val objective: String,
    val questItem: Item,
    val legendaryItem: Item,
)

data class SubRealm(
    val id: String,
    val kind: RealmKind,
    val name: String,
    val biome: Biome,
    val entranceLocationId: String,
    val entryRoomId: String,
    val bossRoomId: String,
    val rooms: Map<String, SubRealmRoom>,
    val quest: SubRealmQuest,
)

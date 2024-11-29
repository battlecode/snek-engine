import { GameFooter } from '../../battlecode/schema/game-footer';
import { GameHeader } from '../../battlecode/schema/game-header';
import { MatchFooter } from '../../battlecode/schema/match-footer';
import { MatchHeader } from '../../battlecode/schema/match-header';
import { Round } from '../../battlecode/schema/round';
/**
 * Events
 * An Event is a single step that needs to be processed.
 * A saved game simply consists of a long list of Events.
 * Events can be divided by either being sent separately (e.g. as separate
 * websocket messages), or by being wrapped with a GameWrapper.
 * A game consists of a series of matches; a match consists of a series of
 * rounds, and is played on a single map. Each round is a single simulation
 * step.
 */
export declare enum Event {
    NONE = 0,
    /**
     * There should only be one GameHeader, at the start of the stream.
     */
    GameHeader = 1,
    /**
     * There should be one MatchHeader at the start of each match.
     */
    MatchHeader = 2,
    /**
     * A single simulation step. A round may be skipped if
     * nothing happens during its time.
     */
    Round = 3,
    /**
     * There should be one MatchFooter at the end of each simulation step.
     */
    MatchFooter = 4,
    /**
     * There should only be one GameFooter, at the end of the stream.
     */
    GameFooter = 5
}
export declare function unionToEvent(type: Event, accessor: (obj: GameFooter | GameHeader | MatchFooter | MatchHeader | Round) => GameFooter | GameHeader | MatchFooter | MatchHeader | Round | null): GameFooter | GameHeader | MatchFooter | MatchHeader | Round | null;
export declare function unionListToEvent(type: Event, accessor: (index: number, obj: GameFooter | GameHeader | MatchFooter | MatchHeader | Round) => GameFooter | GameHeader | MatchFooter | MatchHeader | Round | null, index: number): GameFooter | GameHeader | MatchFooter | MatchHeader | Round | null;

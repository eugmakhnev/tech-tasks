import {mergeIntersectingRanges, binarySearchClosestIndex} from "./main"

describe("Test merge ranges!", () => {
    it("success", () => {
        expect(mergeIntersectingRanges(["1-3", "5-7", "2-4", "8-12", "5-11", "4-4"]))
            .toEqual(["1-4", "5-12"])
    });


    it("one range", () => {
        expect(mergeIntersectingRanges(["1-3"]))
            .toEqual(["1-3"])
    });


    it("empty", () => {
        expect(mergeIntersectingRanges([]))
            .toEqual([])
    });


    it("duplicates", () => {
        expect(mergeIntersectingRanges(["1-3", "2-3", "1-3"]))
            .toEqual(["1-3"])
    });


    it("wrong format", () => {
        expect(() => mergeIntersectingRanges(["1-3.2"])).toThrow(TypeError);
        expect(() => mergeIntersectingRanges(["-1-3"])).toThrow(TypeError);
    });
});


describe("Test binary search!", () => {
    it("no equal elements", () => {
        expect(binarySearchClosestIndex([1, 2, 6, 20, 58], 57, (v) => v))
            .toEqual(4)
    });


    it("two elements array with last value", () => {
        expect(binarySearchClosestIndex([1, 5], 8, (v) => v))
            .toEqual(2)
    });

    it("two elements array with first value", () => {
        expect(binarySearchClosestIndex([2, 5], 1, (v) => v))
            .toEqual(0)
    });

    it("many equal elements, must shift to start of array", () => {
        expect(binarySearchClosestIndex([1, 2, 6, 20, 57, 57, 57, 58], 57, (v) => v))
            .toEqual(4)
    });

    it("empty", () => {
        expect(binarySearchClosestIndex([], 57, (v) => v))
            .toEqual(0)
    });

    it("one element greater than value", () => {
        expect(binarySearchClosestIndex([58], 57, (v) => v))
            .toEqual(0)
    });

    it("one element lower than value", () => {
        expect(binarySearchClosestIndex([56], 57, (v) => v))
            .toEqual(1)
    });
});




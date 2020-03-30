// ToDo:
//  arr - массив строк вида ["1-3","5-7","2-4","8-12","5-11"]
//  Каждая строка в массиве задает интервал [N,M], где N и M - целые числа,
//  включая края. Необходимо написать функцию сигнатуры string[] => string[],
//  которая получает на вход подобный массив, и возвращает массив строк такого же
//  формата, в котором все перекрывающиеся интервалы оптимально склеены и отсортированы.
//  Например, в данном случае должен получиться массив ["1-4","5-12"]
//  Необходимо учесть возможные пограничные случаи, включая невалидный формат
//  входных данных


class Range {
    constructor(
        public readonly start: number,
        public readonly end: number
    ) {
        if (start > end) {
            throw Error("Start of range can not be greater then end!")
        }
    }

    /**
     * Warn! В условиях задачи сказано, что значения могут быть целыми числами. Однако, целые числа это в том числе
     * отрицательные числа. Однако, "-" используется в качестве разделителя. Для простоты будем считать, что используются
     * только натуральные числа и ноль
     *
     * @param range - строка формата "{start}-{end}", например "1-10" , "8-52"
     */
    static fromString(range: string) {
        let [startString, endString, ...rest] = range.split("-");

        const start = Number(startString), end = Number(endString);

        if (rest.length > 0 || !Number.isInteger(start) || !Number.isInteger(end) ) {
            throw new TypeError("Range string is not valid!")
        }

        return new Range(start, end)
    }

    public toString() {
        return `${this.start}-${this.end}`
    }

    static areIntersecting(first: Range, second: Range): boolean {
        return !(second.start > first.end || first.start > second.end)
    }

    static getIntersection(first: Range, second: Range): Range | null {
        if (!Range.areIntersecting(first, second)) {
            return null
        }

        const start = first.start > second.start ? first.start : second.start;
        const end = first.end < second.end ? first.end : second.end;

        return new Range(start, end)
    }

    static getUnion(first: Range, second: Range): Range {
        const start = first.start < second.start ? first.start : second.start;
        const end = first.end > second.end ? first.end : second.end;

        return new Range(start, end)
    }
}

/**
 * Возвращаем ближайший индекс, в который можно вставить новый элемент, с учетом его значения. Используется бинарный
 * поиск для ускорения до O(log n)
 *
 * @param array - массив элементов
 * @param value - значение, для которого мы ищем ближайший индекс для вставки
 * @param selector - функция-трансформер, для извлечения из объекта числа, которое будет использоваться в сравнениях
 */
export function binarySearchClosestIndex<T>(array: T[], value: T, selector: (v: T) => number) {
    // -- utils --
    /**
     * Рекурсивная функция-замыкание, которая позволяет в ряду одинаковых значений найти индекс,
     * который ближе всего к началу массива
     * @param index - текущий индекс
     * @param targetValue - текущее числовое значение для сравнения
     */
    function shiftToStart(index: number, targetValue: number): number {
        const target = array[index - 1];

        if (target && selector(target) === targetValue) {
            return shiftToStart(index - 1, targetValue)
        }

        return index
    }

    const targetValue = selector(value);

    // -- prepare --
    if (array.length === 0) return 0;
    if (array.length === 1) return targetValue > selector(array[0]) ? 1 : 0;

    let start = 0, mid = 0, end = array.length - 1;

    // -- main loop --
    while (start <= end) {
        mid = Math.floor((start + end) / 2);

        const potentiallyClosestValue = selector(array[mid]);

        if (potentiallyClosestValue <= targetValue)
            start = mid + 1;
        else
            end = mid - 1;
    }

    if (targetValue > selector(array[mid])) mid++;

    return shiftToStart(mid, targetValue)
}

export function mergeIntersectingRanges(ranges: string[]): string[] {
    const resultList: Range[] = [];

    // Сложность  O(n) так как .splice пересобирает весь массив. Правда, гарантируется, что .splice происходит всего
    //  один раз за вызов функции
    function insertToResultList(newRange: Range) {
        let indexToInsert = binarySearchClosestIndex(resultList, newRange, (v) => v.start);
        let deleteCount = 0;
        let rangeToInsert = newRange;

        // Edge case: мы фиксируем, что массив отсортирован по start, а значит нужно проверить только один элемент,
        //  который предшествует целевому. Обработка этого условия выстроена так, чтобы после его выполнения просто
        //  корреткно отрабатывал основной алгоритм, который редьюсит текущий массив
        if ((indexToInsert - 1) >= 0) {
            const previousRange = resultList[indexToInsert - 1];
            if (Range.areIntersecting(previousRange, newRange)) {
                indexToInsert -= 1;
                deleteCount = 1;
                rangeToInsert = Range.getUnion(previousRange, newRange)
            }
        }

        while (true) {
            const nextRange = resultList[indexToInsert + deleteCount];

            if (nextRange !== undefined) {
                if (Range.areIntersecting(rangeToInsert, nextRange)) {
                    rangeToInsert = Range.getUnion(rangeToInsert, nextRange);
                    deleteCount += 1;

                    continue
                }
            }

            break
        }

        resultList.splice(indexToInsert, deleteCount, rangeToInsert);
    }

    // -- main loop --
    for (const rangeString of ranges) {
        insertToResultList(Range.fromString(rangeString));
    }

    return resultList.map(r => r.toString())
}

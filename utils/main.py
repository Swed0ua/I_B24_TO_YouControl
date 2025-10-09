def filter_contractors_by_kved(contractors_list, kved_codes, only_main=True):
    """
    Фільтрує список контрагентів за КВЕД кодами та повертає два списки: відповідні та залишок.
    
    :param contractors_list: Список контрагентів з полем economicActivities.
    :param kved_codes: Список КВЕД кодів для фільтрації.
    :param only_main: Якщо True, перевіряє лише основні види діяльності (isMain: true).
    :return: tuple (matching_contractors, remaining_contractors)
    """
    matching_contractors = []
    remaining_contractors = []

    for contractor in contractors_list:
        contractor_kveds = contractor.get("economicActivities", [])

        if contractor_kveds is None:
            contractor_kveds = []

        if only_main:
            contractor_kved_codes = [activity.get("code", "") for activity in contractor_kveds if activity.get("isMain", False)]
        else:
            contractor_kved_codes = [activity.get("code", "") for activity in contractor_kveds]
        
        if any(kved in contractor_kved_codes for kved in kved_codes):
            matching_contractors.append(contractor)
        else:
            remaining_contractors.append(contractor)
    
    return matching_contractors, remaining_contractors

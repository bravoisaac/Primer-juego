#include "Components/TenFeEquipmentComponent.h"

namespace
{
    FTenFeItemDefinition MakeItem(const TCHAR* Id, const TCHAR* Name, ETenFeEquipmentSlot Slot, float Damage, float Defense, float Weight)
    {
        FTenFeItemDefinition Item;
        Item.Id = FName(Id);
        Item.DisplayName = FText::FromString(Name);
        Item.Slot = Slot;
        Item.Damage = Damage;
        Item.Defense = Defense;
        Item.Weight = Weight;
        return Item;
    }
}

UTenFeEquipmentComponent::UTenFeEquipmentComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UTenFeEquipmentComponent::BeginPlay()
{
    Super::BeginPlay();
    InitializeDefaultEquipment();
}

void UTenFeEquipmentComponent::InitializeDefaultEquipment()
{
    if (Weapons.IsEmpty())
    {
        Weapons.Add(MakeItem(TEXT("weathered_sword"), TEXT("Espada desgastada"), ETenFeEquipmentSlot::Weapon, 24.0f, 0.0f, 4.0f));
        Weapons.Add(MakeItem(TEXT("iron_greatsword"), TEXT("Mandoble de hierro"), ETenFeEquipmentSlot::Weapon, 38.0f, 0.0f, 9.0f));
        Weapons.Add(MakeItem(TEXT("hunter_spear"), TEXT("Lanza del cazador"), ETenFeEquipmentSlot::Weapon, 30.0f, 0.0f, 6.0f));
    }

    if (Armors.IsEmpty())
    {
        Armors.Add(MakeItem(TEXT("pilgrim_hood"), TEXT("Capucha del peregrino"), ETenFeEquipmentSlot::Head, 0.0f, 3.0f, 1.5f));
        Armors.Add(MakeItem(TEXT("worn_cuirass"), TEXT("Coraza gastada"), ETenFeEquipmentSlot::Chest, 0.0f, 8.0f, 6.0f));
        Armors.Add(MakeItem(TEXT("iron_greaves"), TEXT("Grebas de hierro"), ETenFeEquipmentSlot::Legs, 0.0f, 5.0f, 4.0f));
    }

    EquippedWeaponIndex = FMath::Clamp(EquippedWeaponIndex, 0, Weapons.Num() - 1);
    EquipArmor(0);
    EquipArmor(1);
    EquipArmor(2);
    OnEquipmentChanged.Broadcast();
}

bool UTenFeEquipmentComponent::EquipWeapon(int32 Index)
{
    if (!Weapons.IsValidIndex(Index))
    {
        return false;
    }

    EquippedWeaponIndex = Index;
    OnEquipmentChanged.Broadcast();
    return true;
}

bool UTenFeEquipmentComponent::EquipArmor(int32 Index)
{
    if (!Armors.IsValidIndex(Index))
    {
        return false;
    }

    switch (Armors[Index].Slot)
    {
        case ETenFeEquipmentSlot::Head: EquippedHeadIndex = Index; break;
        case ETenFeEquipmentSlot::Chest: EquippedChestIndex = Index; break;
        case ETenFeEquipmentSlot::Legs: EquippedLegsIndex = Index; break;
        default: return false;
    }

    OnEquipmentChanged.Broadcast();
    return true;
}

void UTenFeEquipmentComponent::CycleWeapon()
{
    if (!Weapons.IsEmpty())
    {
        EquipWeapon((EquippedWeaponIndex + 1) % Weapons.Num());
    }
}

FTenFeItemDefinition UTenFeEquipmentComponent::GetEquippedWeapon() const
{
    return Weapons.IsValidIndex(EquippedWeaponIndex) ? Weapons[EquippedWeaponIndex] : FTenFeItemDefinition();
}

float UTenFeEquipmentComponent::GetTotalDefense() const
{
    float Defense = 0.0f;
    const int32 Indices[] = {EquippedHeadIndex, EquippedChestIndex, EquippedLegsIndex};
    for (const int32 Index : Indices)
    {
        if (Armors.IsValidIndex(Index))
        {
            Defense += Armors[Index].Defense;
        }
    }
    return Defense;
}

float UTenFeEquipmentComponent::GetEquipmentWeight() const
{
    float Weight = GetEquippedWeapon().Weight;
    const int32 Indices[] = {EquippedHeadIndex, EquippedChestIndex, EquippedLegsIndex};
    for (const int32 Index : Indices)
    {
        if (Armors.IsValidIndex(Index))
        {
            Weight += Armors[Index].Weight;
        }
    }
    return Weight;
}

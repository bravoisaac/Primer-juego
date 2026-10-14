#include "Components/TenFeStatsComponent.h"

UTenFeStatsComponent::UTenFeStatsComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UTenFeStatsComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    SecondsSinceStaminaUse += DeltaTime;
    if (SecondsSinceStaminaUse < StaminaRegenerationDelay || CurrentStamina >= MaxStamina || IsDead())
    {
        return;
    }

    const float Previous = CurrentStamina;
    CurrentStamina = FMath::Min(MaxStamina, CurrentStamina + StaminaRegenerationPerSecond * DeltaTime);
    if (!FMath::IsNearlyEqual(Previous, CurrentStamina))
    {
        OnStaminaChanged.Broadcast(CurrentStamina, MaxStamina);
    }
}

float UTenFeStatsComponent::ApplyDamage(float RawDamage, float Defense)
{
    if (RawDamage <= 0.0f || IsDead())
    {
        return 0.0f;
    }

    const float AppliedDamage = FMath::Max(1.0f, RawDamage - FMath::Max(0.0f, Defense));
    CurrentHealth = FMath::Clamp(CurrentHealth - AppliedDamage, 0.0f, MaxHealth);
    OnHealthChanged.Broadcast(CurrentHealth, MaxHealth);

    if (IsDead())
    {
        OnDeath.Broadcast();
    }

    return AppliedDamage;
}

bool UTenFeStatsComponent::ConsumeStamina(float Amount)
{
    if (Amount <= 0.0f || CurrentStamina < Amount || IsDead())
    {
        return false;
    }

    CurrentStamina -= Amount;
    SecondsSinceStaminaUse = 0.0f;
    OnStaminaChanged.Broadcast(CurrentStamina, MaxStamina);
    return true;
}

void UTenFeStatsComponent::RestoreToFull()
{
    CurrentHealth = MaxHealth;
    CurrentStamina = MaxStamina;
    OnHealthChanged.Broadcast(CurrentHealth, MaxHealth);
    OnStaminaChanged.Broadcast(CurrentStamina, MaxStamina);
}

float UTenFeStatsComponent::GetHealthPercent() const
{
    return MaxHealth > 0.0f ? CurrentHealth / MaxHealth : 0.0f;
}

float UTenFeStatsComponent::GetStaminaPercent() const
{
    return MaxStamina > 0.0f ? CurrentStamina / MaxStamina : 0.0f;
}
